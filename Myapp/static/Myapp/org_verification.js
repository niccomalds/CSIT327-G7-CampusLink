document.addEventListener('DOMContentLoaded', function() {
    // File upload handler
    const fileUploadArea = document.querySelector('.file-upload');
    const fileInput = document.getElementById('verification_document');
    
    if (fileUploadArea && fileInput) {
        fileUploadArea.addEventListener('click', function() {
            fileInput.click();
        });
        
        fileInput.addEventListener('change', function() {
            if (this.files && this.files.length > 0) {
                const fileName = this.files[0].name;
                const fileSize = (this.files[0].size / 1024 / 1024).toFixed(2); // Size in MB
                
                // Update the upload area to show selected file
                fileUploadArea.innerHTML = `
                    <i class="fa-solid fa-file"></i>
                    <p>${fileName}</p>
                    <p><small>${fileSize} MB</small></p>
                `;
            }
        });
    }
    
    // Form validation
    const verificationForm = document.querySelector('.verification-form');
    if (verificationForm) {
        verificationForm.addEventListener('submit', function(e) {
            const emailInput = document.getElementById('institutional_email');
            const email = emailInput.value.trim();
            
            // Email validation
            if (email) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(email)) {
                    alert('Please enter a valid email address.');
                    e.preventDefault();
                    return;
                }
                
                // Check for institutional domains
                const domain = email.split('@')[1].toLowerCase();
                if (!(domain.endsWith('.edu') || domain.endsWith('.ac') || domain.endsWith('.org'))) {
                    if (!confirm('The email domain is not typical for institutions (.edu, .ac, .org). Are you sure you want to proceed?')) {
                        e.preventDefault();
                        return;
                    }
                }
            }
        });
    }
});