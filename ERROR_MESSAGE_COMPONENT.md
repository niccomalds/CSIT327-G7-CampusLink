# Global Error Message Component

## Overview
This component provides a consistent way to display error, warning, info, and success messages throughout the application. It includes automatic styling based on message type, auto-dismissal for non-critical messages, and manual dismissal options.

## Features Implemented

### 1. Error Display System
- Consistent error message component displays with appropriate styling anywhere in the application
- Messages are positioned in the top-right corner of the screen
- Smooth animations for appearance and dismissal

### 2. Error Types with Different Styles
- **Success**: Green gradient background with checkmark icon
- **Error**: Red gradient background with exclamation icon
- **Warning**: Orange gradient background with warning icon
- **Info**: Blue gradient background with info icon

### 3. Auto-dismiss Behavior
- Non-critical messages (success, warning, info) automatically disappear after 5 seconds
- Error messages do not auto-dismiss by default (can be overridden)

### 4. Manual Dismissal
- All messages include an "X" button for manual closure
- Clicking the "X" button immediately dismisses the message

## Installation

### 1. Include CSS and JavaScript files
Add these references to your HTML templates:

```html
<!-- In the <head> section -->
<link rel="stylesheet" href="{% static 'Myapp/error_message.css' %}">

<!-- At the end of the <body> section -->
<script src="{% static 'Myapp/error_message.js' %}"></script>
```

### 2. Add the alert container
Include this container div in your HTML where you want messages to appear:

```html
<div class="alert-container"></div>
```

## Usage

### Shorthand Functions (Recommended)
The component provides convenient global functions for each message type:

```javascript
// Success message
showSuccessMessage('Operation Successful', 'Your changes have been saved.');

// Error message (does not auto-dismiss by default)
showErrorMessage('Error Occurred', 'Failed to save changes. Please try again.');

// Warning message
showWarningMessage('Warning', 'This action cannot be undone.');

// Info message
showInfoMessage('Information', 'New features are available.');
```

### Advanced Usage with Custom Options
You can override default behaviors using the full component API:

```javascript
// Force an error message to auto-dismiss
showErrorMessage('Connection Lost', 'Reconnecting...', true);

// Prevent a success message from auto-dismissing
showSuccessMessage('Upload Complete', 'File uploaded successfully.', false);

// Using the component instance directly
errorMessageComponent.showSuccess('Custom Title', 'Custom message');
errorMessageComponent.showError('Custom Error', 'Detailed error information');
```

## Styling

The component uses gradient backgrounds with distinct colors for each message type:
- Success: Green (#4caf50 to #2e7d32)
- Error: Red (#f44336 to #d32f2f)
- Warning: Orange (#ff9800 to #f57c00)
- Info: Blue (#2196f3 to #1976d2)

All messages include:
- Subtle shadow for depth
- Smooth hover effects
- Responsive design for mobile devices
- Accessible contrast ratios

## Behavior

### Auto-dismiss Rules
- Success, Warning, and Info messages auto-dismiss after 5 seconds
- Error messages do not auto-dismiss by default (to ensure critical errors are seen)
- Maximum of 5 messages displayed at once (older messages are removed)

### Manual Dismissal
- Clicking the "X" button immediately dismisses any message
- Messages slide out smoothly when dismissed

## Integration with Django Messages Framework

To integrate with Django's built-in messages framework, you can convert Django messages to the global component in your templates:

```javascript
// Example of converting Django messages to global component messages
document.addEventListener('DOMContentLoaded', function() {
    // Convert Django success messages
    var successMessages = document.querySelectorAll('.django-success-message');
    successMessages.forEach(function(element) {
        showSuccessMessage('Success', element.textContent);
        element.style.display = 'none'; // Hide original message
    });
    
    // Convert Django error messages
    var errorMessages = document.querySelectorAll('.django-error-message');
    errorMessages.forEach(function(element) {
        showErrorMessage('Error', element.textContent);
        element.style.display = 'none'; // Hide original message
    });
});
```

## Customization

You can customize the behavior by modifying the JavaScript component:
- Adjust `maxVisibleMessages` to change the maximum number of visible messages
- Modify timing in `scheduleAutoDismiss` to change auto-dismiss duration
- Update CSS variables to change colors, sizes, or animations

## Accessibility

The component follows accessibility best practices:
- Proper ARIA attributes (`role="alert"`)
- Sufficient color contrast
- Keyboard navigable close buttons
- Screen reader friendly content structure