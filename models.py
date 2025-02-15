from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    gender = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), nullable=True)
    family_history = db.Column(db.Boolean, nullable=True)
    assessments = db.relationship('Assessment', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Assessment(db.Model):
    __tablename__ = 'assessment'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    phq9_score = db.Column(db.Integer, nullable=False)
    depression_severity = db.Column(db.String(50), nullable=False)
    recommendations = db.Column(db.Text, nullable=True)
    age = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(20), nullable=True)
    family_history = db.Column(db.Boolean, nullable=True)

    def __repr__(self):
        return f'<Assessment {self.id} for User {self.user_id}>'

def init_db():
    db.drop_all()
    db.create_all()
    print("Database initialized successfully!")
