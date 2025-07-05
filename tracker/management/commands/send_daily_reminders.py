from django.core.management.base import BaseCommand
from django.utils import timezone
from tracker.models import DailyReminderSetting, Notification
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

class Command(BaseCommand):
    help = 'Send daily reminders (in-app and email) to users at their chosen time.'

    def handle(self, *args, **options):
        now = timezone.localtime()
        current_time = now.time().replace(second=0, microsecond=0)
        reminders = DailyReminderSetting.objects.filter(reminder_time=current_time)
        sent_count = 0
        for reminder in reminders:
            user = reminder.user
            # In-app notification
            if reminder.send_in_app:
                Notification.objects.create(
                    user=user,
                    type=Notification.NotificationType.DAILY_REMINDER,
                    title="Daily Health Reminder",
                    message="It's time to log your health data!"
                )
            # Email notification
            if reminder.send_email and user.email:
                send_mail(
                    subject="Your Daily Health Reminder",
                    message="Hi {},\n\nThis is your daily reminder to log your health data in the Health Tracker app!".format(user.get_full_name() or user.username),
                    from_email=None,  # Use DEFAULT_FROM_EMAIL
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            sent_count += 1
        self.stdout.write(self.style.SUCCESS(f"Sent {sent_count} daily reminders at {current_time}")) 