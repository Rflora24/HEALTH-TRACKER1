from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from functools import wraps
from django.shortcuts import redirect
from .models import CustomUser

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if request.user.role not in allowed_roles:
                raise PermissionDenied("You don't have permission to access this page.")
                
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def can_access_record(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        record_id = kwargs.get('record_id')
        if not record_id:
            raise PermissionDenied("Record ID is required.")
        
        from .models import HealthRecord
        try:
            record = HealthRecord.objects.get(id=record_id)
            
            # Check if user has permission to access this record
            if (request.user.role == CustomUser.Role.ADMIN or 
                request.user.role == CustomUser.Role.DOCTOR or 
                record.user == request.user):
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied("You don't have permission to access this record.")
                
        except HealthRecord.DoesNotExist:
            raise PermissionDenied("Record not found.")
            
    return _wrapped_view 