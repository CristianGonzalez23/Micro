from pydantic import BaseModel, EmailStr

class NotificationCreate(BaseModel):
    email: EmailStr
    subject: str
    message: str

class Notification(NotificationCreate):
    id: int
