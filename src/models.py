from __future__ import annotations
from datetime import datetime,date
from enum import Enum
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db

import unicodedata
import sqlalchemy as sa
from sqlalchemy import event


class Town(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(255), unique=True, nullable=False)
    
    
    listings:Mapped[list["Listing"]] = relationship(back_populates="town")
    
    users: Mapped[list["User"]] = relationship("User", back_populates="town", foreign_keys="User.town_id")
    subscribers: Mapped[list["User"]] = relationship("User", back_populates="notify_town", foreign_keys="User.notify_town_id")
    

class Role(str, Enum):
    USER = 'user'
    ADMIN = "admin"
    
class Status(str, Enum):
    LOST = "LOST"
    FOUND = "FOUND"
    RETURNED = "RETURNED"
    
class CommentStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    
    
class User(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(sa.String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    role: Mapped[Role] = mapped_column(sa.Enum(Role), name="role_enum", default=Role.USER, nullable=False)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(), default=datetime.utcnow)

    comments: Mapped[list["Comment"]] = relationship(back_populates="commenter", cascade="all, delete-orphan")
    listings: Mapped[list["Listing"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    
    town_id: Mapped[int | None] = mapped_column(sa.ForeignKey("town.id", ondelete="SET NULL"), nullable=True, index=True)
    town: Mapped["Town"] = relationship(back_populates="users", foreign_keys=[town_id])
    
    notify_enabled: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, server_default=sa.text("0"))
    notify_town_id: Mapped[int] = mapped_column(sa.ForeignKey("town.id"), nullable=True, index=True)
    notify_category_id: Mapped[int] = mapped_column(sa.ForeignKey("category.id"), nullable=True, index=True)

    notify_town: Mapped["Town"] = relationship(back_populates="subscribers", foreign_keys=[notify_town_id])
    notify_category: Mapped["Category"] = relationship(back_populates="subscribers", foreign_keys=[notify_category_id])
    
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


def _norm(s: str | None) -> str:
    if not s:
        return ""
    return unicodedata.normalize("NFKC", s).casefold().strip()

class Listing(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    title_search: Mapped[str] = mapped_column(sa.Text(), index=True, nullable=True)
    
    description: Mapped[str] = mapped_column(sa.Text(), nullable=False)
    description_search: Mapped[str] = mapped_column(sa.Text(), index=True, nullable=True)
    
    status: Mapped[Status] = mapped_column(sa.Enum(Status), default=Status.LOST, nullable=False)

    coordinateX:  Mapped[float | None] = mapped_column(sa.Float(), index=True)
    coordinateY: Mapped[float | None] = mapped_column(sa.Float(), index=True)

    images:    Mapped[list["ListingImage"]] = relationship(back_populates="listing", cascade="all, delete-orphan")
    comments:    Mapped[list["Comment"]] = relationship(back_populates="listing", cascade="all, delete-orphan")
    
    location_name: Mapped[Optional[str]] = mapped_column(sa.String(255))
    date_event:    Mapped[date]          = mapped_column(sa.Date(), default=date.today, nullable=False)

    contact_name:  Mapped[Optional[str]] = mapped_column(sa.String(120))
    contact_email: Mapped[Optional[str]] = mapped_column(sa.String(255))
    contact_phone: Mapped[Optional[str]] = mapped_column(sa.String(64))

    owner_id: Mapped[int] = mapped_column(sa.ForeignKey("user.id"), nullable=False)
    owner:    Mapped["User"] = relationship(back_populates="listings")

    created_at: Mapped[datetime] = mapped_column(sa.DateTime(), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    category_id: Mapped[int] = mapped_column(sa.ForeignKey("category.id"), nullable=False, index=True)
    category: Mapped["Category"] = relationship(back_populates="listings")
    
    town_id: Mapped[int | None] = mapped_column(sa.ForeignKey("town.id", ondelete="SET NULL"), nullable=False, index=True)
    town: Mapped["Town"] = relationship(back_populates="listings")


@event.listens_for(Listing, "before_insert")
@event.listens_for(Listing, "before_update")
def _fill_listing_search_cols(mapper, connection, target: "Listing"):
    target.title_search = _norm(target.title)
    target.description_search = _norm(target.description)
    
class Category(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(128), unique=True, nullable=False)
    
    listings: Mapped[list["Listing"]] = relationship(back_populates="category")
    subscribers: Mapped[list["User"]] = relationship("User", back_populates="notify_category", foreign_keys="User.notify_category_id")

    
    
class ListingImage(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    image_path: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    
    listing_id: Mapped[int] = mapped_column(sa.ForeignKey("listing.id"), nullable=False)
    listing: Mapped["Listing"] = relationship(back_populates="images")
    
    
class CommentImage(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    image_path: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    
    comment_id: Mapped[int] = mapped_column(sa.ForeignKey("comment.id"), nullable=False)
    comment: Mapped["Comment"] = relationship(back_populates="images")
    
    
class Comment(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(sa.Text(), nullable=False)
    images: Mapped[list["CommentImage"]] = relationship(back_populates="comment", cascade="all, delete-orphan")
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(), default=datetime.utcnow)
    
    commenter_id: Mapped[int] = mapped_column(sa.ForeignKey("user.id"), nullable=False)
    commenter: Mapped["User"] = relationship(back_populates="comments")
    
    listing_id: Mapped[int] = mapped_column(sa.ForeignKey("listing.id"), nullable=False)
    listing: Mapped["Listing"] = relationship(back_populates="comments")
    
    status: Mapped[CommentStatus] = mapped_column(sa.Enum(CommentStatus), nullable=False, default=CommentStatus.PENDING, server_default="PENDING")
    
    