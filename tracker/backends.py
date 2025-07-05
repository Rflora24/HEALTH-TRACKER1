from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            # Try to fetch the user by email or username
            user = UserModel.objects.get(
                Q(email=username) | Q(username=username)
            )
            
            # Check if account is locked
            if user.account_locked_until and user.account_locked_until > timezone.now():
                return None
                
            # Check password
            if user.check_password(password):
                # Reset failed login attempts on successful login
                user.failed_login_attempts = 0
                user.account_locked_until = None
                user.last_login_ip = self.get_client_ip(request)
                user.save()
                return user
            else:
                # Increment failed login attempts
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= 5:
                    user.account_locked_until = timezone.now() + timezone.timedelta(minutes=15)
                user.save()
                return None
        except UserModel.DoesNotExist:
            return None

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip 