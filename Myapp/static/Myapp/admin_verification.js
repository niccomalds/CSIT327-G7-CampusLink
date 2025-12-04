document.addEventListener('DOMContentLoaded', function() {
    // View document modal
    const viewButtons = document.querySelectorAll('.btn-view');
    const modal = document.getElementById('documentModal');
    const closeModal = document.querySelector('.close-modal');
    
    if (viewButtons.length > 0 && modal) {
        viewButtons.forEach(button => {
            button.addEventListener('click', function() {
                const requestId = this.dataset.requestId;
                const orgName = this.dataset.orgName;
                const email = this.dataset.email;
                const documentUrl = this.dataset.documentUrl;
                
                // Update modal content
                document.getElementById('modalOrgName').textContent = orgName;
                document.getElementById('modalEmail').textContent = email;
                
                const documentPreview = document.getElementById('documentPreview');
                if (documentUrl) {
                    if (documentUrl.toLowerCase().endsWith('.pdf')) {
                        documentPreview.innerHTML = `<iframe src="${documentUrl}" width="100%" height="400px"></iframe>`;
                    } else {
                        documentPreview.innerHTML = `<img src="${documentUrl}" alt="Verification Document">`;
                    }
                } else {
                    documentPreview.innerHTML = '<div class="no-documents">No verification documents provided</div>';
                }
                
                // Show modal
                modal.style.display = 'flex';
            });
        });
        
        // Close modal
        if (closeModal) {
            closeModal.addEventListener('click', function() {
                modal.style.display = 'none';
            });
        }
        
        // Close modal when clicking outside
        window.addEventListener('click', function(event) {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    }
    
    // Approve/Reject buttons
    const approveButtons = document.querySelectorAll('.btn-approve');
    const rejectButtons = document.querySelectorAll('.btn-reject');
    
    if (approveButtons.length > 0) {
        approveButtons.forEach(button => {
            button.addEventListener('click', function() {
                const requestId = this.dataset.requestId;
                if (confirm('Are you sure you want to approve this verification request?')) {
                    // In a real implementation, this would send an AJAX request
                    alert(`Approved request ${requestId}. In a real application, this would update the database.`);
                }
            });
        });
    }
    
    if (rejectButtons.length > 0) {
        rejectButtons.forEach(button => {
            button.addEventListener('click', function() {
                const requestId = this.dataset.requestId;
                if (confirm('Are you sure you want to reject this verification request?')) {
                    // In a real implementation, this would send an AJAX request
                    alert(`Rejected request ${requestId}. In a real application, this would update the database.`);
                }
            });
        });
    }
});