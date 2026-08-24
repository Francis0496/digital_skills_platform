from app.extensions import db
from app.models import Notification

def notify(user_id, message, notification_type=None):
    notification = Notification(user_id=user_id, message=message, notification_type=notification_type)
    db.session.add(notification)
    return notification
