from flask import Blueprint, jsonify
from ..extensions import db
from ..models import Listing

bp = Blueprint("api", __name__)

@bp.get("/listings")
def api_listings():
    listings = Listing.query.all()  # взимаме всички обяви
    data = []
    for it in listings:
        data.append({
            "id": it.id,
            "title": it.title,
            "status": it.status.value,
            "category": it.category.name,
            "lat": it.coordinateX,     # точно за Leaflet
            "lng": it.coordinateY,
            "location_name": it.location_name,
            "url": f"/listings/{it.id}",
        })
    return jsonify(data)
