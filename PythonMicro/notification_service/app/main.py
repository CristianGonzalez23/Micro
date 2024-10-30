from fastapi import FastAPI, HTTPException
from app.models import Notification, NotificationCreate
from app.email_sender import send_email
from app.database import notifications_db

app = FastAPI()

@app.post("/notifications/", response_model=Notification)
async def create_notification(notification: NotificationCreate):
    # Aquí se simula el envío de la notificación por correo electrónico
    send_email(notification.email, notification.subject, notification.message)
    
    # Guardar notificación en la base de datos simulada
    new_notification = {**notification.dict(), "id": len(notifications_db) + 1}
    notifications_db.append(new_notification)
    return new_notification

@app.get("/notifications/", response_model=list[Notification])
async def get_notifications():
    # Retorna todas las notificaciones guardadas
    return notifications_db

@app.get("/notifications/{notification_id}", response_model=Notification)
async def get_notification(notification_id: int):
    for notification in notifications_db:
        if notification["id"] == notification_id:
            return notification
    raise HTTPException(status_code=404, detail="Notification not found")
