import os
from datetime import datetime

from dotenv import load_dotenv
from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   send_from_directory, url_for)
from flask_login import (LoginManager, UserMixin, current_user, login_required,
                         login_user, logout_user)
from flask_sqlalchemy import SQLAlchemy
from twilio.rest import Client
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medtrackr.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads/prescriptions'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# Initialize Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN else None

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))  # Add phone number field
    prescriptions = db.relationship('Prescription', backref='user', lazy=True)
    medications = db.relationship('Medication', backref='user', lazy=True)

class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_name = db.Column(db.String(100))
    date_prescribed = db.Column(db.DateTime, default=datetime.utcnow)
    image_path = db.Column(db.String(200))
    notes = db.Column(db.Text)

class Medication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50))
    frequency = db.Column(db.String(50))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    reminder_time = db.Column(db.Time)
    last_taken = db.Column(db.DateTime)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            name=name
        )
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Fetch user's prescriptions
    prescriptions = Prescription.query.filter_by(user_id=current_user.id).order_by(Prescription.date_prescribed.desc()).all()
    # Fetch user's medications
    medications = Medication.query.filter_by(user_id=current_user.id).order_by(Medication.start_date.desc()).all()
    return render_template('dashboard.html', prescriptions=prescriptions, medications=medications)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/prescription/<int:prescription_id>', methods=['DELETE'])
@login_required
def delete_prescription(prescription_id):
    prescription = Prescription.query.filter_by(id=prescription_id, user_id=current_user.id).first()
    if prescription:
        try:
            # Delete the image file if it exists
            if prescription.image_path:
                image_path = os.path.join('uploads', 'prescriptions', prescription.image_path)
                if os.path.exists(image_path):
                    os.remove(image_path)
            
            # Delete the prescription from the database
            db.session.delete(prescription)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)})
    return jsonify({'success': False, 'error': 'Prescription not found'})

@app.route('/upload_prescription', methods=['POST'])
@login_required
def upload_prescription():
    try:
        # Check if prescription file was uploaded
        if 'prescriptionImage' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'})
        
        file = request.files['prescriptionImage']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type'})
        
        # Get form data
        doctor_name = request.form.get('doctorName')
        prescription_date = request.form.get('prescriptionDate')
        notes = request.form.get('notes')
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        
        # Save the file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Create prescription record
        prescription = Prescription(
            user_id=current_user.id,
            doctor_name=doctor_name,
            date_prescribed=datetime.strptime(prescription_date, '%Y-%m-%d'),
            image_path=unique_filename,
            notes=notes
        )
        
        db.session.add(prescription)
        db.session.commit()
        
        # Return success response with prescription data
        return jsonify({
            'success': True,
            'prescription': {
                'id': prescription.id,
                'doctor_name': prescription.doctor_name,
                'date_prescribed': prescription.date_prescribed.strftime('%B %d, %Y'),
                'image_path': prescription.image_path,
                'notes': prescription.notes
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/uploads/prescriptions/<filename>')
@login_required
def serve_prescription(filename):
    """
    Serve prescription files to authenticated users
    """
    try:
        # Verify that the prescription belongs to the current user
        prescription = Prescription.query.filter_by(
            image_path=filename,
            user_id=current_user.id
        ).first()
        
        if not prescription:
            return jsonify({'error': 'Prescription not found'}), 404
        
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/add_medication', methods=['POST'])
@login_required
def add_medication():
    try:
        # Get form data
        name = request.form.get('medicationName')
        dosage = request.form.get('dosage')
        frequency = request.form.get('frequency')
        reminder_time = request.form.get('reminderTime')
        
        # Create medication record
        medication = Medication(
            user_id=current_user.id,
            name=name,
            dosage=dosage,
            frequency=frequency,
            start_date=datetime.now(),
            reminder_time=datetime.strptime(reminder_time, '%H:%M').time() if reminder_time else None
        )
        
        db.session.add(medication)
        db.session.commit()
        
        # Return success response with medication data
        return jsonify({
            'success': True,
            'medication': {
                'id': medication.id,
                'name': medication.name,
                'dosage': medication.dosage,
                'frequency': medication.frequency,
                'start_date': medication.start_date.strftime('%B %d, %Y'),
                'reminder_time': medication.reminder_time.strftime('%I:%M %p') if medication.reminder_time else None
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/medication/<int:medication_id>', methods=['DELETE'])
@login_required
def delete_medication(medication_id):
    try:
        # Find the medication and verify it belongs to the current user
        medication = Medication.query.filter_by(id=medication_id, user_id=current_user.id).first()
        if not medication:
            return jsonify({'success': False, 'error': 'Medication not found'}), 404
        
        # Delete the medication
        db.session.delete(medication)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Medication deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/medication/<int:medication_id>/reminder', methods=['GET'])
@login_required
def get_medication_reminder(medication_id):
    try:
        medication = Medication.query.filter_by(id=medication_id, user_id=current_user.id).first()
        if not medication:
            print(f"Medication {medication_id} not found")
            return jsonify({'error': 'Medication not found'}), 404
        
        # Get current time
        current_time = datetime.now().time()
        reminder_time = medication.reminder_time
        
        print(f"Checking reminder for medication {medication.name}")
        print(f"Current time: {current_time}")
        print(f"Reminder time: {reminder_time}")
        
        if reminder_time:
            # Convert times to minutes for easier comparison
            current_minutes = current_time.hour * 60 + current_time.minute
            reminder_minutes = reminder_time.hour * 60 + reminder_time.minute
            
            # Check if it's time for the reminder (within 1 minute of the reminder time)
            time_diff = abs(current_minutes - reminder_minutes)
            print(f"Time difference in minutes: {time_diff}")
            
            if time_diff <= 1:  # Within 1 minute of reminder time
                print(f"Reminder triggered for {medication.name}")
                
                # Send SMS notification if phone number is available
                if current_user.phone_number:
                    sms_message = f"MedTrackr Reminder: Time to take {medication.name} - {medication.dosage}"
                    send_sms_notification(current_user.phone_number, sms_message)
                
                return jsonify({
                    'success': True,
                    'medication': {
                        'id': medication.id,
                        'name': medication.name,
                        'dosage': medication.dosage,
                        'frequency': medication.frequency,
                        'reminder_time': reminder_time.strftime('%I:%M %p')
                    }
                })
        
        print(f"No reminder needed for {medication.name}")
        return jsonify({'success': False, 'message': 'Not time for medication yet'})
    except Exception as e:
        print(f"Error in reminder check: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/medication/<int:medication_id>/taken', methods=['POST'])
@login_required
def mark_medication_taken(medication_id):
    medication = Medication.query.filter_by(id=medication_id, user_id=current_user.id).first()
    if not medication:
        return jsonify({'error': 'Medication not found'}), 404
    
    medication.last_taken = datetime.now()
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/update_phone', methods=['POST'])
@login_required
def update_phone():
    try:
        phone_number = request.json.get('phone_number')
        if not phone_number:
            return jsonify({'success': False, 'error': 'Phone number is required'})
        
        # Validate phone number format using re module
        import re
        if not re.match(r'^[+]?[0-9]{10,15}$', phone_number):
            return jsonify({'success': False, 'error': 'Invalid phone number format'})
        
        # Update user's phone number
        current_user.phone_number = phone_number
        db.session.commit()
        
        print(f"Phone number updated for user {current_user.id}: {phone_number}")
        return jsonify({
            'success': True, 
            'message': 'Phone number updated successfully',
            'phone_number': phone_number
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error updating phone number: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

def send_sms_notification(phone_number, message):
    """Send SMS notification using Twilio"""
    if not twilio_client or not phone_number:
        return False
    
    try:
        message = twilio_client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        return True
    except Exception as e:
        print(f"Error sending SMS: {str(e)}")
        return False

def init_app():
    """
    Initialize the application and create necessary directories
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
    
    # Create database tables
    with app.app_context():
        try:
            # Drop all tables first to ensure clean state
            db.drop_all()
            # Create all tables with new schema
            db.create_all()
            print("Database tables created successfully!")
        except Exception as e:
            print(f"Error creating database tables: {str(e)}")
            # If there's an error, try to remove the database file and recreate it
            if os.path.exists('medtrackr.db'):
                os.remove('medtrackr.db')
                db.create_all()
                print("Database recreated successfully!")

if __name__ == '__main__':
    init_app()
    app.run(debug=True) 