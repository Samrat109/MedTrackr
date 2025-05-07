import os
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, messaging, storage


class FirebaseHandler:
    def __init__(self, credentials_path=None):
        """
        Initialize Firebase with credentials
        """
        try:
            if credentials_path and os.path.exists(credentials_path):
                cred = credentials.Certificate(credentials_path)
            else:
                # Use environment variables for credentials
                cred = credentials.Certificate({
                    "type": "service_account",
                    "project_id": os.getenv('FIREBASE_PROJECT_ID'),
                    "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
                    "private_key": os.getenv('FIREBASE_PRIVATE_KEY').replace('\\n', '\n'),
                    "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
                    "client_id": os.getenv('FIREBASE_CLIENT_ID'),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_CERT_URL')
                })
            
            firebase_admin.initialize_app(cred, {
                'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET')
            })
            
            self.bucket = storage.bucket()
        except Exception as e:
            raise Exception(f"Error initializing Firebase: {str(e)}")

    def upload_file(self, file_path, destination_path):
        """
        Upload a file to Firebase Storage
        """
        try:
            blob = self.bucket.blob(destination_path)
            blob.upload_from_filename(file_path)
            
            # Make the file publicly accessible
            blob.make_public()
            
            return blob.public_url
        except Exception as e:
            raise Exception(f"Error uploading file: {str(e)}")

    def download_file(self, source_path, destination_path):
        """
        Download a file from Firebase Storage
        """
        try:
            blob = self.bucket.blob(source_path)
            blob.download_to_filename(destination_path)
            return True
        except Exception as e:
            raise Exception(f"Error downloading file: {str(e)}")

    def delete_file(self, file_path):
        """
        Delete a file from Firebase Storage
        """
        try:
            blob = self.bucket.blob(file_path)
            blob.delete()
            return True
        except Exception as e:
            raise Exception(f"Error deleting file: {str(e)}")

    def send_notification(self, token, title, body, data=None):
        """
        Send a push notification to a specific device
        """
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                token=token
            )
            
            response = messaging.send(message)
            return response
        except Exception as e:
            raise Exception(f"Error sending notification: {str(e)}")

    def send_multicast_notification(self, tokens, title, body, data=None):
        """
        Send push notifications to multiple devices
        """
        try:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                tokens=tokens
            )
            
            response = messaging.send_multicast(message)
            return response
        except Exception as e:
            raise Exception(f"Error sending multicast notification: {str(e)}")

# Example usage:
if __name__ == "__main__":
    # Initialize Firebase handler
    firebase = FirebaseHandler()
    
    # Upload a file
    file_url = firebase.upload_file(
        "path_to_local_file.jpg",
        "prescriptions/prescription_123.jpg"
    )
    print(f"File uploaded to: {file_url}")
    
    # Send a notification
    firebase.send_notification(
        "device_token",
        "Medication Reminder",
        "Time to take your medication!"
    ) 