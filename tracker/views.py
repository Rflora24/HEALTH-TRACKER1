from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import HealthRecordForm, UserProfileForm, DailyReminderSettingForm
from .models import HealthRecord, Notification, DailyReminderSetting, FoodRecommendation
from django.db import models
from datetime import datetime, timedelta
import csv
from io import StringIO
from django.template.loader import render_to_string
from xhtml2pdf import pisa
import tempfile
import os
from django.db.models import Avg, Count, Max, Min
from django.utils import timezone

# Welcome page
def welcome(request):
    return render(request, 'tracker/welcome.html')

# Dashboard (requires login)
@login_required
def dashboard(request):
    # Get all health records for the current user, ordered by date
    records = HealthRecord.objects.filter(user=request.user).order_by('date')
    
    # Weight data
    weight_dates = [record.date.strftime('%Y-%m-%d') for record in records if record.weight is not None]
    weight_values = [record.weight for record in records if record.weight is not None]
    
    # Sleep data
    sleep_dates = [record.date.strftime('%Y-%m-%d') for record in records if record.sleep_hours is not None]
    sleep_values = [record.sleep_hours for record in records if record.sleep_hours is not None]
    
    # Water intake data
    water_dates = [record.date.strftime('%Y-%m-%d') for record in records if record.water_intake is not None]
    water_values = [record.water_intake for record in records if record.water_intake is not None]
    
    # Mood data for pie chart
    mood_counts = {}
    for record in records:
        if record.mood:
            mood_counts[record.mood] = mood_counts.get(record.mood, 0) + 1
    
    mood_labels = list(mood_counts.keys())
    mood_data = list(mood_counts.values())
    
    # Latest record for quick stats
    latest_record = records.last() if records.exists() else None
    
    # Weekly stats (last 7 days)
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    weekly_records = records.filter(date__gte=week_ago)
    
    # Goal progress calculation
    goal_progress = {
        'weight': 0,
        'sleep': 0,
        'water': 0
    }
    
    if latest_record:
        # Weight goal progress
        if request.user.weight_goal and latest_record.weight:
            if request.user.weight_goal > latest_record.weight:
                # Goal is to lose weight
                goal_progress['weight'] = min(100, max(0, ((request.user.weight_goal - latest_record.weight) / (request.user.weight_goal * 0.1)) * 100))
            else:
                # Goal is to gain weight
                goal_progress['weight'] = min(100, max(0, ((latest_record.weight - request.user.weight_goal) / (request.user.weight_goal * 0.1)) * 100))
        
        # Sleep goal progress
        if request.user.sleep_goal and latest_record.sleep_hours:
            goal_progress['sleep'] = min(100, max(0, (latest_record.sleep_hours / request.user.sleep_goal) * 100))
        
        # Water goal progress
        if request.user.water_goal and latest_record.water_intake:
            goal_progress['water'] = min(100, max(0, (latest_record.water_intake / request.user.water_goal) * 100))
    
    weekly_stats = {
        'avg_sleep': weekly_records.aggregate(avg_sleep=models.Avg('sleep_hours'))['avg_sleep'] or 0,
        'avg_water': weekly_records.aggregate(avg_water=models.Avg('water_intake'))['avg_water'] or 0,
        'records_count': weekly_records.count(),
        'goal_achievement': sum(goal_progress.values()) / len(goal_progress) if goal_progress.values() else 0
    }
    
    # Advanced Analytics for Sleep and Water
    # Calculate weekly and monthly averages
    # from datetime import timedelta  # Remove this line if present
    
    # Weekly analytics (last 7 days)
    week_ago = timezone.now().date() - timedelta(days=7)
    weekly_records = records.filter(date__gte=week_ago)
    
    weekly_analytics = {
        'avg_sleep': weekly_records.aggregate(avg=Avg('sleep_hours'))['avg'] or 0,
        'avg_water': weekly_records.aggregate(avg=Avg('water_intake'))['avg'] or 0,
        'best_sleep_day': weekly_records.order_by('sleep_hours').last(),
        'worst_sleep_day': weekly_records.order_by('sleep_hours').first(),
        'best_water_day': weekly_records.order_by('water_intake').last(),
        'worst_water_day': weekly_records.order_by('water_intake').first(),
        'sleep_streak': 0,  # Will calculate below
        'water_streak': 0,  # Will calculate below
    }
    
    # Calculate streaks (consecutive days meeting goals)
    if request.user.sleep_goal:
        sleep_streak = 0
        current_date = timezone.now().date()
        for i in range(7):
            check_date = current_date - timedelta(days=i)
            day_record = records.filter(date=check_date).first()
            if day_record and day_record.sleep_hours >= request.user.sleep_goal:
                sleep_streak += 1
            else:
                break
        weekly_analytics['sleep_streak'] = sleep_streak
    
    if request.user.water_goal:
        water_streak = 0
        current_date = timezone.now().date()
        for i in range(7):
            check_date = current_date - timedelta(days=i)
            day_record = records.filter(date=check_date).first()
            if day_record and day_record.water_intake >= request.user.water_goal:
                water_streak += 1
            else:
                break
        weekly_analytics['water_streak'] = water_streak
    
    # Monthly analytics (last 30 days)
    month_ago = timezone.now().date() - timedelta(days=30)
    monthly_records = records.filter(date__gte=month_ago)
    
    monthly_analytics = {
        'avg_sleep': monthly_records.aggregate(avg=Avg('sleep_hours'))['avg'] or 0,
        'avg_water': monthly_records.aggregate(avg=Avg('water_intake'))['avg'] or 0,
        'total_records': monthly_records.count(),
        'sleep_goal_achieved': monthly_records.filter(sleep_hours__gte=request.user.sleep_goal).count() if request.user.sleep_goal else 0,
        'water_goal_achieved': monthly_records.filter(water_intake__gte=request.user.water_goal).count() if request.user.water_goal else 0,
    }
    
    # Calculate goal achievement percentages
    if monthly_analytics['total_records'] > 0:
        monthly_analytics['sleep_goal_percentage'] = (monthly_analytics['sleep_goal_achieved'] / monthly_analytics['total_records']) * 100
        monthly_analytics['water_goal_percentage'] = (monthly_analytics['water_goal_achieved'] / monthly_analytics['total_records']) * 100
    else:
        monthly_analytics['sleep_goal_percentage'] = 0
        monthly_analytics['water_goal_percentage'] = 0
    
    return render(request, 'tracker/dashboard.html', {
        'weight_dates': weight_dates,
        'weight_values': weight_values,
        'sleep_dates': sleep_dates,
        'sleep_values': sleep_values,
        'water_dates': water_dates,
        'water_values': water_values,
        'mood_labels': mood_labels,
        'mood_data': mood_data,
        'latest_record': latest_record,
        'weekly_stats': weekly_stats,
        'goal_progress': goal_progress,
        'weekly_analytics': weekly_analytics,
        'monthly_analytics': monthly_analytics,
    })

# Registration view
def register(request):
    User = get_user_model()
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if not username or not email or not first_name or not last_name or not password1 or not password2:
            messages.error(request, 'All fields are required.')
        elif password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            user.save()
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('login')
    return render(request, 'tracker/register.html')

# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'tracker/login.html')

# Logout view
def logout_view(request):
    logout(request)
    return redirect('login')

# Add health record
@login_required
def add_health_record(request):
    if request.method == 'POST':
        form = HealthRecordForm(request.POST)
        form.instance.user = request.user  # Set user before validation
        form.instance.created_by = request.user
        form.instance.last_modified_by = request.user
        if form.is_valid():
            record = form.save()
            messages.success(request, 'Health record added successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = HealthRecordForm()
    return render(request, 'tracker/add_health_record.html', {'form': form, 'title': 'Add Health Record'})

# User profile
@login_required
def user_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('user_profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'tracker/profile.html', {
        'form': form,
        'user': request.user
    })

# Notifications
@login_required
def notifications(request):
    # Get user's notifications, ordered by most recent
    user_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Mark notifications as read when user visits the page
    unread_notifications = user_notifications.filter(is_read=False)
    unread_notifications.update(is_read=True)
    
    return render(request, 'tracker/notifications.html', {
        'notifications': user_notifications,
        'unread_count': unread_notifications.count()
    })

# Mood journal
@login_required
def get_mood_journal(request):
    return render(request, 'tracker/dashboard.html')

# API: Get unread notifications
@login_required
def get_unread_notifications(request):
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'unread_count': unread_count})

@login_required
def mark_notification_read(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False}, status=404)

@login_required
def mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'success': True})

def create_achievement_notification(user, achievement_type, message):
    """Create an achievement notification for the user"""
    notification = Notification.objects.create(
        user=user,
        type=Notification.NotificationType.WEIGHT_MILESTONE if 'weight' in achievement_type else Notification.NotificationType.WEIGHT_GOAL,
        title=f"Achievement Unlocked: {achievement_type.title()}",
        message=message
    )
    return notification

@login_required
def daily_reminder(request):
    """Send daily reminder to log health data"""
    # Check if user has logged data today
    today = datetime.now().date()
    has_logged_today = HealthRecord.objects.filter(user=request.user, date=today).exists()
    
    if not has_logged_today:
        # Create reminder notification
        notification = Notification.objects.create(
            user=request.user,
            type=Notification.NotificationType.DAILY_REMINDER,
            title="Daily Health Check-in",
            message="Don't forget to log your health data today! Track your sleep, water intake, weight, and mood."
        )
        messages.success(request, "Daily reminder set! Check your notifications.")
    else:
        messages.info(request, "Great job! You've already logged your health data today.")
    
    return redirect('dashboard')

# Export functionality
@login_required
def export_dashboard(request):
    """Export dashboard - shows export options"""
    return render(request, 'tracker/export_dashboard.html')

@login_required
def export_csv(request):
    """Export health records to CSV"""
    # Get date range from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Get user's health records
    records = HealthRecord.objects.filter(user=request.user).order_by('date')
    
    if start_date:
        records = records.filter(date__gte=start_date)
    if end_date:
        records = records.filter(date__lte=end_date)
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="health_records_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Date', 'Sleep Hours', 'Water Intake (L)', 'Weight (kg)', 
        'Height (cm)', 'Mood', 'Notes', 'Created At'
    ])
    
    for record in records:
        writer.writerow([
            record.date,
            record.sleep_hours,
            record.water_intake,
            record.weight or '',
            record.height or '',
            record.mood,
            record.notes or '',
            record.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response

@login_required
def export_pdf(request):
    """Export health report to PDF using xhtml2pdf"""
    records = HealthRecord.objects.filter(user=request.user).order_by('-date')[:30]
    total_records = HealthRecord.objects.filter(user=request.user).count()
    avg_sleep = records.aggregate(avg=models.Avg('sleep_hours'))['avg_sleep__avg'] or 0
    avg_water = records.aggregate(avg=models.Avg('water_intake'))['avg_water__avg'] or 0
    avg_weight = records.aggregate(avg=models.Avg('weight'))['avg_weight__avg'] or 0
    context = {
        'user': request.user,
        'records': records,
        'total_records': total_records,
        'avg_sleep': round(avg_sleep, 1),
        'avg_water': round(avg_water, 1),
        'avg_weight': round(avg_weight, 1) if avg_weight else None,
        'generated_date': datetime.now().strftime('%B %d, %Y'),
        'date_range': f"Last {len(records)} records"
    }
    html_string = render_to_string('tracker/pdf_report.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="health_report_{datetime.now().strftime('%Y%m%d')}.pdf"'
    pisa_status = pisa.CreatePDF(html_string, dest=response)
    if pisa_status.err:
        messages.error(request, "Error generating PDF.")
        return redirect('export_dashboard')
    return response

@login_required
def export_summary(request):
    """Export weekly/monthly summary"""
    period = request.GET.get('period', 'week')  # week or month
    
    # Calculate date range
    today = datetime.now().date()
    if period == 'week':
        start_date = today - timedelta(days=7)
        period_name = "Weekly"
    else:
        start_date = today - timedelta(days=30)
        period_name = "Monthly"
    
    # Get records for the period
    records = HealthRecord.objects.filter(
        user=request.user, 
        date__gte=start_date
    ).order_by('date')
    
    # Calculate summary stats
    summary = {
        'period': period_name,
        'start_date': start_date,
        'end_date': today,
        'total_records': records.count(),
        'avg_sleep': records.aggregate(avg=models.Avg('sleep_hours'))['avg_sleep__avg'] or 0,
        'avg_water': records.aggregate(avg=models.Avg('water_intake'))['avg_water__avg'] or 0,
        'avg_weight': records.aggregate(avg=models.Avg('weight'))['avg_weight__avg'] or 0,
        'mood_distribution': records.values('mood').annotate(count=models.Count('mood'))
    }
    
    return render(request, 'tracker/export_summary.html', summary)

@login_required
def daily_reminder_settings(request):
    try:
        reminder_setting = request.user.reminder_setting
    except DailyReminderSetting.DoesNotExist:
        reminder_setting = None

    if request.method == 'POST':
        form = DailyReminderSettingForm(request.POST, instance=reminder_setting)
        if form.is_valid():
            reminder = form.save(commit=False)
            reminder.user = request.user
            reminder.save()
            messages.success(request, 'Daily reminder settings updated!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DailyReminderSettingForm(instance=reminder_setting)

    return render(request, 'tracker/daily_reminder_settings.html', {
        'form': form,
        'reminder_setting': reminder_setting
    })

# Error handlers
def handler404(request, exception, template_name='tracker/404.html'):
    response = render(request, template_name, status=404)
    return response

def handler500(request, template_name='tracker/500.html'):
    response = render(request, template_name, status=500)
    return response

def food_recommendations(request):
    foods = FoodRecommendation.objects.all()
    return render(request, 'tracker/food_recommendations.html', {'foods': foods}) 