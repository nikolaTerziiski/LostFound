from flask import session
from flask_login import current_user
from app.models import User

class TestAuth:
    
    def test_successful_registration(self, client, init_database):
        response = client.post('/register', data={
            'email': 'new.user@test.com',
            'password': 'password123',
            'confirm_pass': 'password123'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert 'Успешна регистрация! Моля влезте'.encode('utf-8') in response.data

        user = User.query.filter_by(email='new.user@test.com').first()
        assert user is not None
        assert user.email == 'new.user@test.com'

    def test_duplicate_registration(self, client, init_database):
        response = client.post('/register', data={
            'email': 'testuser@example.com',
            'password': 'password123',
            'confirm_pass': 'password123'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert 'Този имейл вече е регистриран'.encode('utf-8') in response.data

    def test_successful_login_and_logout(self, client, init_database):
        response = client.post('/login', data={
            'email': 'testuser@example.com',
            'password': 'password'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert 'Здравей, testuser@example.com'.encode('utf-8') in response.data
        
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        assert 'Здравей, testuser@example.com'.encode('utf-8') not in response.data
        assert 'Вход'.encode('utf-8') in response.data

    def test_current_user_and_session_after_login(self, client, init_database):
        with client:
            client.get('/') 
            assert not current_user.is_authenticated

            client.post('/login', data={
                'email': 'testuser@example.com',
                'password': 'password'
            })

            assert current_user.is_authenticated
            assert current_user.email == 'testuser@example.com'
            assert session['_user_id'] == str(current_user.id)
            
            client.get('/logout')
            
            assert not current_user.is_authenticated
            assert '_user_id' not in session