// Utility Functions
function formatDate(date) {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatTime(time) {
    return new Date(time).toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Notification Functions
function requestNotificationPermission() {
    if ('Notification' in window) {
        Notification.requestPermission();
    }
}

function showNotification(title, options = {}) {
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(title, options);
    }
}

// Medication Reminder Functions
function scheduleMedicationReminder(medication) {
    const reminderTime = new Date(medication.reminderTime);
    const now = new Date();
    
    if (reminderTime > now) {
        const timeUntilReminder = reminderTime - now;
        setTimeout(() => {
            showNotification('Medication Reminder', {
                body: `Time to take ${medication.name} - ${medication.dosage}`,
                icon: '/static/images/logo.png'
            });
        }, timeUntilReminder);
    }
}

// Prescription Upload Functions
function handlePrescriptionUpload(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            // Preview the image
            const preview = document.createElement('img');
            preview.src = e.target.result;
            preview.style.maxWidth = '100%';
            preview.style.marginTop = '1rem';
            
            const container = event.target.parentElement;
            container.appendChild(preview);
        };
        reader.readAsDataURL(file);
    }
}

// Form Validation Functions
function validateMedicationForm(form) {
    const name = form.querySelector('#medicationName').value;
    const dosage = form.querySelector('#dosage').value;
    const frequency = form.querySelector('#frequency').value;
    const reminderTime = form.querySelector('#reminderTime').value;

    if (!name || !dosage || !frequency || !reminderTime) {
        showError('Please fill in all required fields');
        return false;
    }

    return true;
}

function validatePrescriptionForm(form) {
    const doctorName = form.querySelector('#doctorName').value;
    const prescriptionDate = form.querySelector('#prescriptionDate').value;
    const prescriptionImage = form.querySelector('#prescriptionImage').files[0];

    if (!doctorName || !prescriptionDate || !prescriptionImage) {
        showError('Please fill in all required fields');
        return false;
    }

    return true;
}

// Error Handling
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'flash-message error';
    errorDiv.textContent = message;
    
    document.querySelector('.form-container').prepend(errorDiv);
    
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Request notification permission on page load
    requestNotificationPermission();

    // Add event listeners for prescription upload preview
    const prescriptionUpload = document.querySelector('#prescriptionImage');
    if (prescriptionUpload) {
        prescriptionUpload.addEventListener('change', handlePrescriptionUpload);
    }

    // Add form validation
    const medicationForm = document.querySelector('#addMedicationForm');
    if (medicationForm) {
        medicationForm.addEventListener('submit', function(e) {
            if (!validateMedicationForm(this)) {
                e.preventDefault();
            }
        });
    }

    const prescriptionForm = document.querySelector('#uploadPrescriptionForm');
    if (prescriptionForm) {
        prescriptionForm.addEventListener('submit', function(e) {
            if (!validatePrescriptionForm(this)) {
                e.preventDefault();
            }
        });
    }
}); 