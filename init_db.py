import os
import sys

from app import app, db


def init_database():
    """
    Initialize the database and create necessary directories
    """
    # Create necessary directories
    directories = [
        'uploads',
        'uploads/prescriptions',
        'reports',
        'static/images'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Create database tables
    with app.app_context():
        try:
            # Drop all existing tables
            db.drop_all()
            print("Dropped existing tables")
            
            # Create all tables
            db.create_all()
            print("Database tables created successfully!")
        except Exception as e:
            print(f"Error creating database tables: {str(e)}")
            # If there's an error, try to remove the database file and recreate it
            if os.path.exists('medtrackr.db'):
                os.remove('medtrackr.db')
                db.create_all()
                print("Database recreated successfully!")

if __name__ == "__main__":
    init_database() 