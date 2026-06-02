import os
import time
from fastapi.testclient import TestClient

os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')
os.environ.setdefault('SECRET_KEY', 'test-secret')

from fastapi_app import main, crud, schemas
from fastapi_app.database import init_db, SessionLocal


def setup_module(module):
    # initialize in-memory DB
    init_db()


def test_register_login_and_task_crud():
    client = TestClient(main.app)

    # create admin directly
    db = SessionLocal()
    admin_in = schemas.UserCreate(username='admin', email='admin@example.com', password='adminpass')
    admin = crud.create_user(db, admin_in, role='admin')

    # register user via API
    res = client.post('/api/v1/auth/register', json={'username':'alice','email':'alice@example.com','password':'alicepass'})
    assert res.status_code == 200

    # login user
    res = client.post('/api/v1/auth/login', data={'username':'alice','password':'alicepass'})
    assert res.status_code == 200
    token = res.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # create task
    res = client.post('/api/v1/tasks', json={'title':'Test Task','description':'desc'}, headers=headers)
    assert res.status_code == 200
    task = res.json()
    assert task['title'] == 'Test Task'

    # another user registration
    res = client.post('/api/v1/auth/register', json={'username':'bob','email':'bob@example.com','password':'bobpass'})
    assert res.status_code == 200
    res = client.post('/api/v1/auth/login', data={'username':'bob','password':'bobpass'})
    bob_token = res.json()['access_token']
    bob_headers = {'Authorization': f'Bearer {bob_token}'}

    # bob attempts to update alice's task -> should be forbidden (403)
    res = client.put(f"/api/v1/tasks/{task['id']}", json={'title':'Hacked','description':'x'}, headers=bob_headers)
    assert res.status_code == 403

    # admin can list users
    res = client.post('/api/v1/auth/login', data={'username':'admin','password':'adminpass'})
    assert res.status_code == 200
    admin_token = res.json()['access_token']
    admin_headers = {'Authorization': f'Bearer {admin_token}'}
    res = client.get('/api/v1/users', headers=admin_headers)
    assert res.status_code == 200
    users = res.json()
    assert any(u['username']=='alice' for u in users)
