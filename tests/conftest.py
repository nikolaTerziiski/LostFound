import pytest

from src import create_app, db
from src.models import Category, Role, Status, Town, User


@pytest.fixture(scope='function')
def app():
    app = create_app(config_class='testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def init_database(app):
    with app.app_context():
        db.create_all()
        user = User(email='testuser@example.com', role=Role.USER)
        user.set_password('password')
        admin = User(email='admin@example.com', role=Role.ADMIN)
        admin.set_password('adminpass')
        sofia = Town(name="София")
        keys = Category(name="Ключове")
        notifier_user = User(
            email='notifier@example.com', 
            role=Role.USER, 
            notify_enabled=True,
            notify_town_id=1,
            notify_category_id=1
        )
        notifier_user.set_password('password')
        db.session.add_all([user, admin, notifier_user, sofia, keys])
        db.session.commit()

        yield db

        db.session.remove()
        db.drop_all()