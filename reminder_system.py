import threading
import time
from datetime import datetime, timedelta

import schedule

from firebase_handler import FirebaseHandler


class ReminderSystem:
    def __init__(self, firebase_handler=None):
        """
        Initialize the reminder system
        """
        self.firebase_handler = firebase_handler or FirebaseHandler()
        self.reminders = {}
        self.running = False
        self.thread = None

    def add_reminder(self, user_id, medication_id, medication_name, dosage, frequency, reminder_time):
        """
        Add a new medication reminder
        """
        try:
            # Create reminder object
            reminder = {
                'user_id': user_id,
                'medication_id': medication_id,
                'medication_name': medication_name,
                'dosage': dosage,
                'frequency': frequency,
                'reminder_time': reminder_time,
                'last_notified': None
            }
            
            # Store reminder
            self.reminders[medication_id] = reminder
            
            # Schedule the reminder
            self._schedule_reminder(reminder)
            
            return True
        except Exception as e:
            raise Exception(f"Error adding reminder: {str(e)}")

    def remove_reminder(self, medication_id):
        """
        Remove a medication reminder
        """
        try:
            if medication_id in self.reminders:
                # Clear the scheduled job
                schedule.clear(medication_id)
                # Remove from reminders dictionary
                del self.reminders[medication_id]
                return True
            return False
        except Exception as e:
            raise Exception(f"Error removing reminder: {str(e)}")

    def update_reminder(self, medication_id, **kwargs):
        """
        Update an existing reminder
        """
        try:
            if medication_id in self.reminders:
                # Update reminder properties
                for key, value in kwargs.items():
                    if key in self.reminders[medication_id]:
                        self.reminders[medication_id][key] = value
                
                # Reschedule the reminder
                self._schedule_reminder(self.reminders[medication_id])
                return True
            return False
        except Exception as e:
            raise Exception(f"Error updating reminder: {str(e)}")

    def _schedule_reminder(self, reminder):
        """
        Schedule a reminder using the schedule library
        """
        def notify():
            # Get user's notification token from database
            # This is a placeholder - you would need to implement this
            user_token = "user_notification_token"
            
            # Send notification
            self.firebase_handler.send_notification(
                user_token,
                "Medication Reminder",
                f"Time to take {reminder['medication_name']} - {reminder['dosage']}"
            )
            
            # Update last notified time
            reminder['last_notified'] = datetime.now()
        
        # Schedule the reminder
        schedule.every().day.at(reminder['reminder_time']).do(notify).tag(reminder['medication_id'])

    def start(self):
        """
        Start the reminder system in a separate thread
        """
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_scheduler)
            self.thread.daemon = True
            self.thread.start()

    def stop(self):
        """
        Stop the reminder system
        """
        self.running = False
        if self.thread:
            self.thread.join()

    def _run_scheduler(self):
        """
        Run the scheduler loop
        """
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def get_reminders(self, user_id=None):
        """
        Get all reminders or reminders for a specific user
        """
        if user_id:
            return {k: v for k, v in self.reminders.items() if v['user_id'] == user_id}
        return self.reminders

    def get_next_reminder(self, user_id):
        """
        Get the next upcoming reminder for a user
        """
        user_reminders = self.get_reminders(user_id)
        if not user_reminders:
            return None
        
        now = datetime.now()
        next_reminder = None
        next_time = None
        
        for reminder in user_reminders.values():
            reminder_time = datetime.strptime(reminder['reminder_time'], '%H:%M').time()
            reminder_datetime = datetime.combine(now.date(), reminder_time)
            
            if reminder_datetime > now:
                if next_time is None or reminder_datetime < next_time:
                    next_time = reminder_datetime
                    next_reminder = reminder
        
        return next_reminder

# Example usage:
if __name__ == "__main__":
    # Initialize reminder system
    reminder_system = ReminderSystem()
    
    # Add a reminder
    reminder_system.add_reminder(
        user_id="user123",
        medication_id="med123",
        medication_name="Amoxicillin",
        dosage="500mg",
        frequency="twice daily",
        reminder_time="14:00"
    )
    
    # Start the reminder system
    reminder_system.start()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Stop the reminder system
        reminder_system.stop() 