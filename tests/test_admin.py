# tests/test_admin.py
from src.extensions import db
from sqlalchemy import select
from src.models import User


class TestAdmin:

    def test_admin_dashboard_unauthenticated(self, client):
        response = client.get('/admin/', follow_redirects=True)
        assert response.status_code == 200
        assert 'Вход'.encode('utf-8') in response.data

    def test_admin_dashboard_as_normal_user(self, client, init_database):
        client.post('/login', data={'email': 'testuser@example.com', 'password': 'password'})
        response = client.get('/admin/')
        assert response.status_code == 403

    def test_admin_dashboard_as_admin(self, client, init_database):
        client.post('/login', data={'email': 'admin@example.com', 'password': 'adminpass'})
        response = client.get('/admin/', follow_redirects=True)
        assert response.status_code == 200
        assert 'Overview'.encode('utf-8') in response.data

    def test_admin_can_delete_user(self, client, init_database):
        client.post('/login', data={'email': 'admin@example.com', 'password': 'adminpass'})
        
        user_to_delete = db.session.scalar(select(User).filter_by(email='testuser@example.com'))
        assert user_to_delete is not None
        user_id = user_to_delete.id

        response = client.post(f'/admin/user/{user_id}/delete', follow_redirects=True)

        assert response.status_code == 200
        assert db.session.get(User, user_id) is None

    def test_admin_cannot_delete_self(self, client, init_database):
        client.post('/login', data={'email': 'admin@example.com', 'password': 'adminpass'})
        admin_user = db.session.scalar(select(User).filter_by(email='admin@example.com'))
        admin_id = admin_user.id

        response = client.post(f'/admin/user/{admin_id}/delete', follow_redirects=True)

        assert response.status_code == 200
        assert 'Не можете да изтриете собствения си администраторски акаунт.'.encode('utf-8') in response.data
        assert db.session.get(User, admin_id) is not None
        
    def test_admin_delete_non_existent_user(self, client, init_database):
        client.post('/login', data={'email': 'admin@example.com', 'password': 'adminpass'})
    
        non_existent_user_id = 9999
        response = client.post(f'/admin/user/{non_existent_user_id}/delete', follow_redirects=True)

        assert response.status_code == 200
        assert 'Потребителят не е намерен.'.encode('utf-8') in response.data
        assert b'admin@example.com' in response.data
