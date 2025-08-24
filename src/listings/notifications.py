from flask import current_app, url_for
from flask_mail import Message
import sqlalchemy as sa

from ..extensions import mail
from ..models import User, Listing


def notify_all_users(listing: "Listing") -> int:

    query = User.query.filter(
        User.notify_enabled.is_(True),
        sa.or_(
            User.notify_town_id == listing.town_id,
            User.notify_category_id == listing.category_id,
        ), User.id != listing.owner_id).with_entities(User.email)

    emails = sorted({e for (e, ) in query.all()})

    if not emails:
        return 0

    print(emails)
    link = url_for("listings.detail", listing_id=listing.id, _external=True)
    subject = f"[Lost&Found] Нова обява: {listing.title}"
    text = f"Появи се нова обява:\n{listing.title}\n{listing.location_name or ''}\n{link}\n"
    html = f"""
            <p>Появи се нова обява, която отговаря на вашите предпочитания.</p>
            <p><b>{listing.title}</b> — {listing.location_name or ''}</p>
            <p><a href="{link}">Виж обявата</a></p>
        """
    msg = Message(subject=subject, recipients=emails, body=text, html=html)
    mail.send(msg)
    current_app.logger.info("Sent notify for listing %s to %d user(s)",
                            listing.id, len(emails))
    return len(emails)
