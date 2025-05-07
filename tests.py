import os
import unittest
from datetime import datetime

from app import Medication, Prescription, User, app, db


class TestMedTrackr(unittest.TestCase):
    def setUp(self):
        """
        Set up test environment
        """
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()
            
            # Create test user
            user = User(
                email='test@example.com',
                password_hash='test_password',
                name='Test User'
            )
            db.session.add(user)
            db.session.commit()
            
            self.user_id = user.id

    def tearDown(self):
        """
        Clean up test environment
        """
        with app.app_context():
            db.session.remove()
            db.drop_all()
        
        # Remove test database
        if os.path.exists('test.db'):
            os.remove('test.db')

    def test_user_creation(self):
        """
        Test user creation
        """
        with app.app_context():
            user = User.query.filter_by(email='test@example.com').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.name, 'Test User')

    def test_prescription_creation(self):
        """
        Test prescription creation
        """
        with app.app_context():
            prescription = Prescription(
                user_id=self.user_id,
                doctor_name='Dr. Smith',
                date_prescribed=datetime.now(),
                notes='Test prescription'
            )
            db.session.add(prescription)
            db.session.commit()
            
            saved_prescription = Prescription.query.filter_by(user_id=self.user_id).first()
            self.assertIsNotNone(saved_prescription)
            self.assertEqual(saved_prescription.doctor_name, 'Dr. Smith')

    def test_medication_creation(self):
        """
        Test medication creation
        """
        with app.app_context():
            medication = Medication(
                user_id=self.user_id,
                name='Amoxicillin',
                dosage='500mg',
                frequency='Twice daily',
                start_date=datetime.now()
            )
            db.session.add(medication)
            db.session.commit()
            
            saved_medication = Medication.query.filter_by(user_id=self.user_id).first()
            self.assertIsNotNone(saved_medication)
            self.assertEqual(saved_medication.name, 'Amoxicillin')
            self.assertEqual(saved_medication.dosage, '500mg')

    def test_user_medication_relationship(self):
        """
        Test user-medication relationship
        """
        with app.app_context():
            user = User.query.get(self.user_id)
            
            medication = Medication(
                name='Amoxicillin',
                dosage='500mg',
                frequency='Twice daily',
                start_date=datetime.now()
            )
            user.medications.append(medication)
            db.session.commit()
            
            self.assertEqual(len(user.medications), 1)
            self.assertEqual(user.medications[0].name, 'Amoxicillin')

    def test_user_prescription_relationship(self):
        """
        Test user-prescription relationship
        """
        with app.app_context():
            user = User.query.get(self.user_id)
            
            prescription = Prescription(
                doctor_name='Dr. Smith',
                date_prescribed=datetime.now(),
                notes='Test prescription'
            )
            user.prescriptions.append(prescription)
            db.session.commit()
            
            self.assertEqual(len(user.prescriptions), 1)
            self.assertEqual(user.prescriptions[0].doctor_name, 'Dr. Smith')

if __name__ == '__main__':
    unittest.main() 