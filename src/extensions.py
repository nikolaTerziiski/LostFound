"""Flask extensions initialization."""

from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}


class Base(DeclarativeBase):
    """Declarative base for SQLAlchemy models."""


metadata = MetaData(naming_convention=convention)
db: SQLAlchemy = SQLAlchemy(model_class=Base, metadata=metadata)
migrate: Migrate = Migrate()
login_manager: LoginManager = LoginManager()
mail: Mail = Mail()
csrf: CSRFProtect = CSRFProtect()
