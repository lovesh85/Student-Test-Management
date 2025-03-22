// Common JavaScript functions for the application

// Toggle password visibility
function togglePasswordVisibility(passwordField, toggleButton) {
    const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordField.setAttribute('type', type);
    
    // Toggle icon
    const icon = toggleButton.querySelector('i');
    icon.classList.toggle('fa-eye');
    icon.classList.toggle('fa-eye-slash');
}

// Format phone number as user types
function formatPhoneNumber(input) {
    // Remove all non-numeric characters
    let phoneNumber = input.value.replace(/\D/g, '');
    
    // Format phone number with proper spacing/dashes
    if (phoneNumber.length > 0) {
        if (phoneNumber.length <= 3) {
            phoneNumber = phoneNumber;
        } else if (phoneNumber.length <= 6) {
            phoneNumber = phoneNumber.slice(0, 3) + '-' + phoneNumber.slice(3);
        } else {
            phoneNumber = phoneNumber.slice(0, 3) + '-' + phoneNumber.slice(3, 6) + '-' + phoneNumber.slice(6, 10);
        }
        
        input.value = phoneNumber;
    }
}

// Document ready function
document.addEventListener('DOMContentLoaded', function() {
    // Initialize phone formatting if phone field exists
    const phoneInput = document.getElementById('phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', function() {
            formatPhoneNumber(this);
        });
    }
});
