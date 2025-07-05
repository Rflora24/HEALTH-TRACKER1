import csv
import json
from datetime import datetime
from django.http import HttpResponse
from django.utils.text import slugify
from django.utils.translation import gettext as _
from .models import HealthRecord, CustomUser

def export_health_records(request, user_id):
    """
    Export health records to CSV format.
    
    Args:
        request: Django request object
        user_id: ID of the user whose records to export
        
    Returns:
        HttpResponse with CSV file attachment
    """
    user = get_object_or_404(CustomUser, id=user_id)
    records = HealthRecord.objects.filter(user=user).order_by('date')
    
    # Create filename with timestamp
    filename = f"health_records_{slugify(user.username)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    writer.writerow([
        _('Date'),
        _('Sleep Hours'),
        _('Water Intake (L)'),
        _('Weight (kg)'),
        _('Height (cm)'),
        _('Mood'),
        _('Created By'),
        _('Last Modified By'),
        _('Created At'),
        _('Last Modified At')
    ])
    
    for record in records:
        writer.writerow([
            record.date,
            record.sleep_hours,
            record.water_intake,
            record.weight,
            record.height,
            record.get_mood_display(),
            record.created_by.username,
            record.last_modified_by.username,
            record.created_at,
            record.last_modified_at
        ])
    
    return response

def export_to_json(request, user_id):
    """
    Export health records to JSON format.
    
    Args:
        request: Django request object
        user_id: ID of the user whose records to export
        
    Returns:
        HttpResponse with JSON file attachment
    """
    user = get_object_or_404(CustomUser, id=user_id)
    records = HealthRecord.objects.filter(user=user).order_by('date')
    
    # Create filename with timestamp
    filename = f"health_records_{slugify(user.username)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # Prepare data for JSON
    data = []
    for record in records:
        data.append({
            'date': record.date.isoformat(),
            'sleep_hours': record.sleep_hours,
            'water_intake': record.water_intake,
            'weight': record.weight,
            'height': record.height,
            'mood': record.get_mood_display(),
            'created_by': record.created_by.username,
            'last_modified_by': record.last_modified_by.username,
            'created_at': record.created_at.isoformat(),
            'last_modified_at': record.last_modified_at.isoformat()
        })
    
    # Create JSON response
    response = HttpResponse(json.dumps(data, indent=2), content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response
