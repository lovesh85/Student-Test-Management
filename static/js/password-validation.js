document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm_password');
    const passwordFeedback = document.getElementById('password-feedback');
    const confirmPasswordFeedback = document.getElementById('confirm-password-feedback');
    
    // Validate password as user types
    passwordInput.addEventListener('input', validatePassword);
    confirmPasswordInput.addEventListener('input', checkPasswordMatch);
    
    function validatePassword() {
        const password = passwordInput.value;
        let feedback = '';
        
        // Check password length
        if (password.length < 8) {
            feedback += '<div class="text-danger">Password must be at least 8 characters long</div>';
        } else {
            feedback += '<div class="text-success">✓ Password length is good</div>';
        }
        
        // Check for special character
        if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
            feedback += '<div class="text-danger">Password must contain at least one special character</div>';
        } else {
            feedback += '<div class="text-success">✓ Password contains special character</div>';
        }
        
        // Display feedback
        passwordFeedback.innerHTML = feedback;
        
        // If confirm password is not empty, check match again
        if (confirmPasswordInput.value !== '') {
            checkPasswordMatch();
        }
    }
    
    function checkPasswordMatch() {
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;
        
        if (confirmPassword === '') {
            confirmPasswordFeedback.innerHTML = '';
            return;
        }
        
        if (password !== confirmPassword) {
            confirmPasswordFeedback.innerHTML = '<div class="text-danger">Passwords do not match</div>';
        } else {
            confirmPasswordFeedback.innerHTML = '<div class="text-success">✓ Passwords match</div>';
        }
    }
});
