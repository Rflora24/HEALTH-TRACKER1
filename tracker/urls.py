from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add/', views.add_health_record, name='add_health_record'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('mood-journal/', views.get_mood_journal, name='mood_journal'),
    path('notifications/', views.notifications, name='notifications'),
    path('api/unread-notifications/', views.get_unread_notifications, name='unread_notifications'),
    path('api/mark-notification-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('api/mark-all-notifications-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('daily-reminder/', views.daily_reminder, name='daily_reminder'),
    path('daily-reminder-settings/', views.daily_reminder_settings, name='daily_reminder_settings'),
    path('profile/', views.user_profile, name='user_profile'),
    
    # Password Reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='tracker/password_reset.html',
        email_template_name='tracker/password_reset_email.html',
        subject_template_name='tracker/password_reset_subject.txt'
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='tracker/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='tracker/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='tracker/password_reset_complete.html'
    ), name='password_reset_complete'),
    path('export/', views.export_dashboard, name='export_dashboard'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
    path('export/summary/', views.export_summary, name='export_summary'),
    path('food-recommendations/', views.food_recommendations, name='food_recommendations'),
]
