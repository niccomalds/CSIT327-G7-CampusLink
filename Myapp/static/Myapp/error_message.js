// Global Error Message Component

class ErrorMessageComponent {
  constructor() {
    this.container = this.createContainer();
    this.messageQueue = [];
    this.maxVisibleMessages = 5;
  }

  createContainer() {
    let container = document.querySelector('.alert-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'alert-container';
      document.body.appendChild(container);
    }
    return container;
  }

  // Show an error message
  showMessage(type, title, message, autoDismiss = true) {
    const alert = this.createAlertElement(type, title, message);
    this.container.appendChild(alert);
    
    // Limit the number of visible messages
    this.manageMessageCount();
    
    // Set up auto-dismissal if requested
    if (autoDismiss) {
      this.scheduleAutoDismiss(alert, type);
    }
    
    return alert;
  }

  createAlertElement(type, title, message) {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.setAttribute('role', 'alert');
    
    // Icon based on type
    const icons = {
      success: 'fa-circle-check',
      error: 'fa-circle-exclamation',
      warning: 'fa-triangle-exclamation',
      info: 'fa-circle-info'
    };
    
    alert.innerHTML = `
      <div class="alert-icon">
        <i class="fas ${icons[type] || icons.info}"></i>
      </div>
      <div class="alert-content">
        <div class="alert-title">${title}</div>
        <div class="alert-message">${message}</div>
      </div>
      <button class="alert-close" aria-label="Close">
        <i class="fas fa-times"></i>
      </button>
    `;
    
    // Add event listener for manual dismissal
    const closeButton = alert.querySelector('.alert-close');
    closeButton.addEventListener('click', () => {
      this.dismissMessage(alert);
    });
    
    return alert;
  }

  manageMessageCount() {
    const alerts = this.container.querySelectorAll('.alert');
    if (alerts.length > this.maxVisibleMessages) {
      // Remove the oldest message
      const oldestAlert = alerts[0];
      this.dismissMessage(oldestAlert);
    }
  }

  scheduleAutoDismiss(alert, type) {
    // Don't auto-dismiss error messages by default
    const shouldAutoDismiss = type !== 'error';
    
    if (shouldAutoDismiss) {
      setTimeout(() => {
        this.dismissMessage(alert);
      }, 5000); // 5 seconds
    }
  }

  dismissMessage(alert) {
    // Add dismissing animation class
    alert.classList.add('dismissing');
    
    // Remove after animation completes
    setTimeout(() => {
      if (alert.parentNode === this.container) {
        this.container.removeChild(alert);
      }
    }, 300);
  }

  // Convenience methods for different message types
  showSuccess(title, message, autoDismiss = true) {
    return this.showMessage('success', title, message, autoDismiss);
  }

  showError(title, message, autoDismiss = false) {
    return this.showMessage('error', title, message, autoDismiss);
  }

  showWarning(title, message, autoDismiss = true) {
    return this.showMessage('warning', title, message, autoDismiss);
  }

  showInfo(title, message, autoDismiss = true) {
    return this.showMessage('info', title, message, autoDismiss);
  }
}

// Initialize the global error message component
const errorMessageComponent = new ErrorMessageComponent();

// Make it globally available
window.errorMessageComponent = errorMessageComponent;

// Also provide shorthand functions for convenience
window.showSuccessMessage = (title, message) => errorMessageComponent.showSuccess(title, message);
window.showErrorMessage = (title, message) => errorMessageComponent.showError(title, message);
window.showWarningMessage = (title, message) => errorMessageComponent.showWarning(title, message);
window.showInfoMessage = (title, message) => errorMessageComponent.showInfo(title, message);

// Example usage:
// showSuccessMessage('Success', 'Your changes have been saved!');
// showErrorMessage('Error', 'Failed to save changes. Please try again.');
// showWarningMessage('Warning', 'This action cannot be undone.');
// showInfoMessage('Information', 'New features are available.');

console.log('Global Error Message Component loaded');