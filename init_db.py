from app import app, db
from models import User, Assessment

def init_db():
    with app.app_context():
        # Drop all existing tables
        db.drop_all()
        
        # Create all tables with new schema
        db.create_all()
        
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
