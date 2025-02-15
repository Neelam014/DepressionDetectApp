import os

class Config:
    # Flask configuration
    SECRET_KEY = os.urandom(24)
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'sqlite:///virtuwellness.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ML Models configuration
    MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
    SESSION_PROTECTION = 'strong'
    
    # Security configuration
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.urandom(24)
