from app import create_app      # Импортира фабриката за Flask app (с всички разширения, модели и миграции)
from app.extensions import db
from app.models import User, Listing, Status, Role, Category
from datetime import date

app = create_app()

with app.app_context():
    # 1) Създава "admin" потребител само ако не съществува
    admin = User.query.filter_by(email="admin@admin.com").first()
    if not admin:
        admin = User(email="admin@admin.com", role=Role.ADMIN)
        admin.set_password("admin")
        db.session.add(admin)
        db.session.flush()

    
    fixed_categories = ["Животно", "Предмет", "Ключове"]
    categories: dict[str, Category] = {}
    for name in fixed_categories:
        cat = Category.query.filter_by(name=name).first()
        if not cat:
            cat = Category(name=name)
            db.session.add(cat)
            db.session.flush()
        categories[name] = cat
    # 2) Създава две примерни обяви, само ако липсват
    if not Listing.query.first():
        l1 = Listing(
            title="Изгубено портмоне",
            description="Черно портмоне около НДК.",
            category=categories["Предмет"],
            status=Status.LOST,
            coordinateX=42.688,    # ако още си с coordinateX/coordinateY, смени
            coordinateY=23.319,
            date_event=date.today(),
            owner=admin,
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
        )
        db.session.add_all([l1, l2, l3])
        db.session.commit()
        print("Seed OK")
    else:
        print("Already seeded")
