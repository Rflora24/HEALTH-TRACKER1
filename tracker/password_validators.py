from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re

class CustomPasswordValidator:
    """Custom password validator with multiple security checks."""
    
    def validate(self, password, user=None):
        """
        Validate that the password meets security requirements.
        
        Args:
            password: The password to validate
            user: The user object (optional)
            
        Raises:
            ValidationError: If password doesn't meet requirements
        """
        # Minimum length
        if len(password) < 8:
            raise ValidationError(
                _('Password must be at least 8 characters long.'),
                code='password_too_short',
            )
            
        # Maximum length
        if len(password) > 128:
            raise ValidationError(
                _('Password must not exceed 128 characters.'),
                code='password_too_long',
            )
            
        # At least one uppercase letter
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _('Password must contain at least one uppercase letter.'),
                code='password_no_uppercase',
            )
            
        # At least one lowercase letter
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _('Password must contain at least one lowercase letter.'),
                code='password_no_lowercase',
            )
            
        # At least one digit
        if not re.search(r'[0-9]', password):
            raise ValidationError(
                _('Password must contain at least one number.'),
                code='password_no_number',
            )
            
        # No spaces
        if ' ' in password:
            raise ValidationError(
                _('Password must not contain spaces.'),
                code='password_contains_spaces',
            )
            
    def get_help_text(self):
        """Return help text for password requirements."""
        return _(
            "Your password must contain at least 8 characters, including uppercase and lowercase letters, "
            "and numbers. It must not contain spaces."
        )
