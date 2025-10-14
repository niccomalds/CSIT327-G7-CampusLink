import datetime
from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect

class AutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)

        now = datetime.datetime.now(datetime.timezone.utc)  # use timezone-aware datetime
        last_activity = request.session.get('last_activity')

        if last_activity:
            try:
                last_activity_time = datetime.datetime.fromisoformat(last_activity)
                # Make sure it's timezone-aware too
                if last_activity_time.tzinfo is None:
                    last_activity_time = last_activity_time.replace(tzinfo=datetime.timezone.utc)

                elapsed = (now - last_activity_time).total_seconds()
                if elapsed > getattr(settings, 'AUTO_LOGOUT_DELAY', 300):  # default 5 mins
                    logout(request)
                    return redirect('login')

            except (ValueError, TypeError):
                # If session data is malformed, reset it safely
                request.session['last_activity'] = now.isoformat()

        request.session['last_activity'] = now.isoformat()
        return self.get_response(request)
