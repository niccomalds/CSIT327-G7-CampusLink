from .models import Application

def check_duplicate_application(student, posting_id):
    """
    SUB-TASK 1: Duplicate Check
    Given I submit application, When API checks for duplicates, 
    Then system prevents multiple applications to same posting.
    """
    return Application.objects.filter(student=student, posting_id=posting_id).exists()

def get_user_application_status(user, posting_id):
    """
    SUB-TASK 3: Application Status Display  
    Given I previously applied, When I view posting,
    Then system can check if I already applied.
    """
    try:
        return Application.objects.get(student=user, posting_id=posting_id)
    except Application.DoesNotExist:
        return None

def can_user_apply(user, posting_id):
    """
    SUB-TASK 2: Duplicate Warning
    Given I already applied to posting, When I try to apply again,
    Then system returns appropriate message.
    """
    if not user.is_authenticated:
        return False, None, "Please log in to apply"
    
    existing_app = get_user_application_status(user, posting_id)
    if existing_app:
        return False, existing_app, "You have already applied to this opportunity"
    
    return True, None, "Apply now"