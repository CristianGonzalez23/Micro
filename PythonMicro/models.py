from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Nuevos campos
    personal_page = db.Column(db.String(255))
    nickname = db.Column(db.String(80))
    contact_public = db.Column(db.Boolean, default=False)
    address = db.Column(db.String(255))
    biography = db.Column(db.Text)
    organization = db.Column(db.String(255))
    country = db.Column(db.String(80))
    social_links = db.Column(db.JSON)  # Almacenar enlaces de redes sociales como JSON

    def __repr__(self):
        return f'<User {self.username}>'