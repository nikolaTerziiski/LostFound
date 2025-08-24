from flask import session
from flask_login import current_user

from sqlalchemy import select

from src import db
from src.models import Town, User



class TestAuth:

    def test_successful_registration(self, client, init_database):
        response = client.post('/register',
                               data={
                                   'email': 'new.user@test.com',
                                   'password': 'password123',
                                   'confirm_pass': 'password123'
                               },
                               follow_redirects=True)

        assert response.status_code == 200
        assert 'Успешна регистрация! Моля влезте'.encode(
            'utf-8') in response.data

        user = db.session.execute(
            select(User).where(User.email == 'new.user@test.com')
        ).scalar_one_or_none()
        assert user is not None
        assert user.email == 'new.user@test.com'

    def test_duplicate_registration(self, client, init_database):
        response = client.post('/register',
                               data={
                                   'email': 'testuser@example.com',
                                   'password': 'password123',
                                   'confirm_pass': 'password123'
                               },
                               follow_redirects=True)

        assert response.status_code == 200
        assert 'Този имейл вече е регистриран'.encode('utf-8') in response.data

    def test_successful_login_and_logout(self, client, init_database):
        response = client.post('/login',
                               data={
                                   'email': 'testuser@example.com',
                                   'password': 'password'
                               },
                               follow_redirects=True)

        assert response.status_code == 200
        assert 'Здравей, testuser@example.com'.encode('utf-8') in response.data

        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        assert 'Здравей, testuser@example.com'.encode(
            'utf-8') not in response.data
        assert 'Вход'.encode('utf-8') in response.data

    def test_current_user_and_session_after_login(self, client, init_database):
        with client:
            client.get('/')
            assert not current_user.is_authenticated

            client.post('/login',
                        data={
                            'email': 'testuser@example.com',
                            'password': 'password'
                        })

            assert current_user.is_authenticated
            assert current_user.email == 'testuser@example.com'
            assert session['_user_id'] == str(current_user.id)

            client.get('/logout')

            assert not current_user.is_authenticated
            assert '_user_id' not in session

    def test_user_can_access_account_page(self, client, init_database):
        client.post('/login',
                    data={
                        'email': 'testuser@example.com',
                        'password': 'password'
                    })
        response = client.get('/account')
        assert response.status_code == 200
        assert b'Profile Settings' in response.data

    def test_user_can_update_town(self, client, init_database):
        client.post('/login',
                    data={
                        'email': 'testuser@example.com',
                        'password': 'password'
                    })
        plovdiv = Town(name="Пловдив")
        db.session.add(plovdiv)
        db.session.commit()

        response = client.post('/account',
                               data={'town_id': plovdiv.id},
                               follow_redirects=True)

        assert response.status_code == 200
        assert 'Профилът е обновен.'.encode('utf-8') in response.data

        user = db.session.scalar(
            select(User).where(User.email == 'testuser@example.com')
        )
        assert user.town.name == "Пловдив"

    def test_user_can_change_password_successfully(self, client,
                                                   init_database):
        client.post('/login',
                    data={
                        'email': 'testuser@example.com',
                        'password': 'password'
                    })

        response = client.post('/account',
                               data={
                                   'old_password': 'password',
                                   'new_password': 'new_password123',
                                   'repeat_password': 'new_password123'
                               },
                               follow_redirects=True)

        assert response.status_code == 200
        assert 'Паролата е сменена.'.encode('utf-8') in response.data
        user = db.session.scalar(
            select(User).where(User.email == 'testuser@example.com')
        )
        assert user.check_password('new_password123')
        assert not user.check_password('password')

    def test_password_change_fails_with_wrong_old_password(
            self, client, init_database):
        client.post('/login',
                    data={
                        'email': 'testuser@example.com',
                        'password': 'password'
                    })

        response = client.post('/account',
                               data={
                                   'old_password': 'wrong_old_password',
                                   'new_password': 'new_password123',
                                   'repeat_password': 'new_password123'
                               },
                               follow_redirects=True)

        assert response.status_code == 200
        assert 'Невалидна текуща парола.'.encode('utf-8') in response.data

    def test_password_change_fails_with_mismatched_new_passwords(
            self, client, init_database):
        client.post('/login',
                    data={
                        'email': 'testuser@example.com',
                        'password': 'password'
                    })

        response = client.post('/account',
                               data={
                                   'old_password': 'password',
                                   'new_password': 'new_password123',
                                   'repeat_password': 'another_password456'
                               },
                               follow_redirects=True)

        assert response.status_code == 200
        assert 'Паролите не съвпадат.'.encode('utf-8') in response.data
