import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.all_models import Notification, User

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])


class NotificationResponse(BaseModel):
    id: str
    message: str
    lu: str
    created_at: str

    class Config:
        from_attributes = True


def creer_notification(db: Session, user_id: str, message: str):
    """Fonction utilitaire : à appeler depuis d'autres routers pour générer une notification automatique."""
    notif = Notification(
        id=str(uuid.uuid4()),
        user_id=user_id,
        message=message,
        lu="non",
        created_at=datetime.now(timezone.utc),
    )
    db.add(notif)
    db.commit()


@router.get("/", response_model=List[NotificationResponse])
def lister_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notifs = (
        db.query(Notification)
        .filter(Notification.user_id == str(current_user.id))
        .order_by(Notification.created_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": str(n.id),
            "message": n.message,
            "lu": n.lu,
            "created_at": n.created_at.isoformat() if n.created_at else "",
        }
        for n in notifs
    ]


@router.put("/{notif_id}/lu")
def marquer_lu(
    notif_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notif = (
        db.query(Notification)
        .filter(Notification.id == notif_id, Notification.user_id == str(current_user.id))
        .first()
    )
    if not notif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification introuvable")

    notif.lu = "oui"
    db.commit()
    return {"message": "Notification marquée comme lue"}
