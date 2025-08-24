"""API routes for exposing listings in JSON format."""

from datetime import date

from flask import Blueprint, jsonify, url_for
from sqlalchemy import select

from ..extensions import db
from ..models import Listing, Status

bp = Blueprint("api", __name__)


@bp.get("/listings")
def api_listings():
    """Return all active listings as JSON."""
    stmt = select(Listing).where(Listing.status != Status.RETURNED)
    listings = db.session.execute(stmt).scalars().all()
    data = []
    for it in listings:
        data.append({
            "id":
            it.id,
            "title":
            it.title,
            "status":
            it.status.value,
            "category":
            it.category.name,
            "lat":
            it.coordinateX,  # точно за Leaflet
            "lng":
            it.coordinateY,
            "location_name":
            it.location_name,
            "url":
            f"/listings/{it.id}",
            "picture":
            url_for('uploaded_file', filename=it.images[0].image_path)
            if len(it.images) > 0 else None,
            "date":
            it.created_at.strftime("%d.%m.%Y %H:%M")
        })
    return jsonify(data)
