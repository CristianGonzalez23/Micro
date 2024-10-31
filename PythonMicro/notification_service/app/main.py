import smtplib
from email.mime.text import MIMEText
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse
from app.models import Notification, NotificationCreate
from app.email_sender import send_email
from app.database import notifications_db

app = FastAPI()

@app.post('/notifications/', response_model=Notification)
async def create_notification(notification: NotificationCreate):
    # Aquí se simula el envío de la notificación por correo electrónico
    send_email(notification.email, notification.subject, notification.message)
    
    # Guardar notificación en la base de datos simulada
    new_notification = {**notification.dict(), "id": len(notifications_db) + 1}
    notifications_db.append(new_notification)
    return new_notification

@app.get('/notifications/', response_model=list[Notification])
async def get_notifications():
    # Retorna todas las notificaciones guardadas
    return notifications_db

@app.get('/notifications/{notification_id}', response_model=Notification)
async def get_notification(notification_id: int):
    for notification in notifications_db:
        if notification["id"] == notification_id:
            return notification
    raise HTTPException(status_code=404, detail="Notification not found")

# Endpoint para Prometheus /metrics en formato de texto
@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    # Ejemplo de métrica básica que se puede monitorear
    notifications_count = len(notifications_db)
    metrics_text = (
        "# HELP notifications_count Número de notificaciones\n"
        "# TYPE notifications_count gauge\n"
        f"notifications_count {notifications_count}\n"
    )
    return PlainTextResponse(metrics_text, media_type="text/plain; charset=utf-8")

# Función para enviar notificaciones por correo electrónico
def send_email_notification(to_email, subject, body):
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = 'cristianr.gonzalezi@uqvirtual.edu.co'
        msg['To'] = to_email

        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        from_email = "cristianr.gonzalezi@uqvirtual.edu.co"
        password = "Crisgonza_20"

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, to_email, msg.as_string())

        print(f'Email sent to: {to_email}')
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")

# Endpoint para recibir alertas de Prometheus y enviar notificaciones
@app.post('/alert')
async def receive_alert(request: Request):
    alert = await request.json()
    for alert in alert['alerts']:
        email = "djgortegaro@gmail.com"  # Cambia esto al correo electrónico del destinatario
        subject = f"Alerta: Alert Notification"
        body = f"description: {alert['annotations']['description']}\n" \
               f"summary: {alert['annotations']['summary']}\n"
        
        # Enviar notificación por correo electrónico
        send_email_notification(email, subject, body)
        
        # Guardar notificación en la base de datos simulada
        new_notification = {
            "id": len(notifications_db) + 1,
            "email": email,
            "subject": subject,
            "message": body
        }
        notifications_db.append(new_notification)
    
    return {"status": "success"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)