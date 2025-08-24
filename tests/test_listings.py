from datetime import date
from src.extensions import db
from src.models import Listing, User

class TestListings:
    def test_create_listing_as_authenticated_user(self, client, init_database):
        client.post('/login', data={'email': 'testuser@example.com', 'password': 'password'})
        response = client.post('/listings/create', data={
            'title': 'Изгубен портфейл',
            'description': 'Кафяв кожен портфейл.',
            'category_id': 1,
            'town_id': 1,
            'date_event': date.today().strftime('%Y-%m-%d')
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_user_can_edit_own_listing(self, client, init_database):
        client.post('/login', data={'email': 'testuser@example.com', 'password': 'password'})
        user = User.query.filter_by(email='testuser@example.com').first()
        listing = Listing(title='Старо заглавие', description='Старо описание', owner_id=user.id, category_id=1, town_id=1, date_event=date.today())
        db.session.add(listing)
        db.session.commit()

        response = client.post(f'/listings/edit/{listing.id}', data={
            'title': 'Ново заглавие', 'description': 'Ново описание', 'category_id': 1, 'town_id': 1
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_user_can_delete_own_listing(self, client, init_database):
        client.post('/login', data={'email': 'testuser@example.com', 'password': 'password'})
        user = User.query.filter_by(email='testuser@example.com').first()
        listing = Listing(title='За изтриване', description='Описание', owner_id=user.id, category_id=1, town_id=1, date_event=date.today())
        db.session.add(listing)
        db.session.commit()
        listing_id = listing.id

        response = client.post(f'/listings/delete/{listing_id}', follow_redirects=True)
        assert response.status_code == 200
        assert db.session.get(Listing, listing_id) is None

    def test_unauthenticated_user_cannot_edit_listing(self, client, init_database):
        user = User.query.first()
        listing = Listing(title='Обява за тест', description='Описание', owner_id=user.id, category_id=1, town_id=1, date_event=date.today())
        db.session.add(listing)
        db.session.commit()
        
        response = client.get(f'/listings/edit/{listing.id}', follow_redirects=True)
        assert 'Вход'.encode('utf-8') in response.data

    def test_user_cannot_edit_others_listing(self, client, init_database):
        admin = User.query.filter_by(email='admin@example.com').first()
        listing = Listing(title='Обява на админ', description='Описание', owner_id=admin.id, category_id=1, town_id=1, date_event=date.today())
        db.session.add(listing)
        db.session.commit()
        
        client.post('/login', data={'email': 'testuser@example.com', 'password': 'password'})
        response = client.get(f'/listings/edit/{listing.id}')
        assert response.status_code == 403

    def test_unauthenticated_user_cannot_delete_listing(self, client, init_database):
        user = User.query.first()
        listing = Listing(title='Обява за тест', description='Описание', owner_id=user.id, category_id=1, town_id=1, date_event=date.today())
        db.session.add(listing)
        db.session.commit()
        
        response = client.post(f'/listings/delete/{listing.id}')
        assert response.status_code == 302
        assert '/login' in response.location
        
    def test_user_cannot_delete_others_listing(self, client, init_database):
        admin = User.query.filter_by(email='admin@example.com').first()
        listing = Listing(title='Обява на админ', description='Описание', owner_id=admin.id, category_id=1, town_id=1, date_event=date.today())
        db.session.add(listing)
        db.session.commit()
        
        client.post('/login', data={'email': 'testuser@example.com', 'password': 'password'})
        response = client.post(f'/listings/delete/{listing.id}')
        assert response.status_code == 403
        
    def test_search_and_filter_listings(self, client, init_database):
        user = User.query.first()
        listing1 = Listing(title="Намерено синьо портмоне", description="...", owner_id=user.id, category_id=1, town_id=1, date_event=date.today())
        listing2 = Listing(title="Изгубени черни ключове", description="...", owner_id=user.id, category_id=1, town_id=1, date_event=date.today())
        db.session.add_all([listing1, listing2])
        db.session.commit()

        response = client.get('/listings/?q=портмоне')
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        assert "синьо портмоне" in html
        assert "черни ключове" not in html

    def test_post_comment_on_listing(self, client, init_database):
        client.post('/login', data={'email': 'testuser@example.com', 'password': 'password'})
        admin = User.query.filter_by(email='admin@example.com').first()
        listing = Listing(title="Обява за коментар", description="...", owner_id=admin.id, category_id=1, town_id=1, date_event=date.today())
        
        db.session.add(listing)
        db.session.commit()
        
        response = client.post(f'/listings/{listing.id}', data={
            'text': 'Това е тестов коментар.'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert 'Успешно оставихте коментар!'.encode('utf-8') in response.data
        assert 'Това е тестов коментар.'.encode('utf-8') in response.data

    def test_user_can_mark_listing_as_returned(self, client, init_database):
        client.post('/login', data={'email': 'testuser@example.com', 'password': 'password'})
        user = User.query.filter_by(email='testuser@example.com').first()
        listing = Listing(title="За връщане", description="...", owner_id=user.id, category_id=1, town_id=1, date_event=date.today())
        db.session.add(listing)
        db.session.commit()
        response = client.post(f'/listings/{listing.id}/returned', follow_redirects=True)

        assert response.status_code == 200
        assert 'Обявата е отбелязана като НАМЕРЕНА'.encode('utf-8') in response.data
    
        updated_listing = db.session.get(Listing, listing.id)
        assert updated_listing.status.value == "RETURNED"