"""Seed the database with initial data (towns, categories, admin user, demo listings)."""

from datetime import date

from src import create_app
from src.extensions import db
from src.models import Category, Listing, Role, Status, Town, User
from sqlalchemy import select

app = create_app()

with app.app_context():
    towns_seed = ["София", "Пловдив", "Варна", "Бургас"]
    towns_by_name: dict[str, Town] = {}

    for name in towns_seed:
        stmt = select(Town).where(Town.name == name)
        t = db.session.execute(stmt).scalar_one_or_none()
        if not t:
            t = Town(name=name)
            db.session.add(t)
            db.session.flush()
        towns_by_name[name] = t

    stmt = select(User).where(User.email == "admin@admin.com")
    admin = db.session.execute(stmt).scalar_one_or_none()
    if not admin:
        admin = User(email="admin@admin.com", role=Role.ADMIN, town=towns_by_name["София"])
        admin.set_password("admin")
        db.session.add(admin)
        db.session.flush()
    else:
        if admin.town is None:
            admin.town = towns_by_name["София"]

    fixed_categories = ["Животно", "Предмет", "Ключове"]
    categories: dict[str, Category] = {}
    for name in fixed_categories:
        stmt = select(Category).where(Category.name == name)
        cat = db.session.execute(stmt).scalar_one_or_none()
        if not cat:
            cat = Category(name=name)
            db.session.add(cat)
            db.session.flush()
        categories[name] = cat

    # seed demo listings if empty
    stmt = select(Listing)
    if not db.session.execute(stmt).first():
        l1 = Listing(
            title="Изгубено портмоне",
            description="Черно портмоне около НДК.",
            category=categories["Предмет"],
            status=Status.LOST,
            coordinateX=42.688,
            coordinateY=23.319,
            date_event=date.today(),
            owner=admin,
            town=towns_by_name["София"],
        )
        l2 = Listing(
            title="Намерена котка",
            description="Сива котка с нашийник в Младост 1.",
            category=categories["Животно"],
            status=Status.FOUND,
            coordinateX=42.650,
            coordinateY=23.377,
            date_event=date.today(),
            owner=admin,
            town=towns_by_name["София"],
        )
        l3 = Listing(
            title="Намерени ключове",
            description="Ключове с червен ключодържател на Орлов мост.",
            category=categories["Ключове"],
            status=Status.FOUND,
            coordinateX=42.693,
            coordinateY=23.335,
            date_event=date.today(),
            owner=admin,
            town=towns_by_name["София"],
        )
        db.session.add_all([l1, l2, l3])
        db.session.commit()
        print("Seed OK (towns, admin, categories, listings)")
    else:
        updated = 0
        stmt = select(Listing).where(Listing.town_id.is_(None))
        for l in db.session.execute(stmt).scalars().all():
            l.town = towns_by_name["София"]
            updated += 1
        if updated:
            db.session.commit()
        print(f"Already seeded (backfilled town for {updated} listings)")
