from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        DOCTOR = 'DOCTOR', 'Doctor'
        PATIENT = 'PATIENT', 'Patient'

    class Gender(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
        OTHER = 'O', 'Other'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.PATIENT
    )
    email = models.EmailField(_('email address'), unique=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True, null=True)
    age = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1, message='Age must be at least 1'),
            MaxValueValidator(120, message='Age must be less than 120')
        ],
        help_text='Age in years'
    )
    gender = models.CharField(
        max_length=1,
        choices=Gender.choices,
        null=True,
        blank=True,
        help_text='Gender'
    )
    weight_goal = models.FloatField(null=True, blank=True, help_text="Target weight in kg")
    sleep_goal = models.FloatField(
        null=True, 
        blank=True, 
        validators=[
            MinValueValidator(4, message='Sleep goal must be at least 4 hours'),
            MaxValueValidator(12, message='Sleep goal must be less than 12 hours')
        ],
        help_text="Target sleep hours per night"
    )
    water_goal = models.FloatField(
        null=True, 
        blank=True, 
        validators=[
            MinValueValidator(1, message='Water goal must be at least 1 liter'),
            MaxValueValidator(10, message='Water goal must be less than 10 liters')
        ],
        help_text="Target water intake in liters per day"
    )
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)

    class Meta:
        permissions = [
            ("can_view_patient_records", "Can view patient records"),
            ("can_edit_patient_records", "Can edit patient records"),
            ("can_delete_patient_records", "Can delete patient records"),
        ]

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class HealthRecord(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    sleep_hours = models.FloatField(
        validators=[
            MinValueValidator(0, message='Sleep hours must be between 0 and 24'),
            MaxValueValidator(24, message='Sleep hours must be between 0 and 24')
        ]
    )
    water_intake = models.FloatField(
        validators=[
            MinValueValidator(0, message='Water intake cannot be negative'),
            MaxValueValidator(10, message='Please enter a realistic water intake amount')
        ]
    )
    weight = models.FloatField(
        validators=[
            MinValueValidator(20, message='Weight must be at least 20 kg'),
            MaxValueValidator(300, message='Weight must be less than 300 kg')
        ],
        null=True,
        blank=True,
        help_text='Weight in kilograms'
    )
    height = models.FloatField(
        validators=[
            MinValueValidator(100, message='Height must be at least 100 cm'),
            MaxValueValidator(250, message='Height must be less than 250 cm')
        ],
        null=True,
        blank=True,
        help_text='Height in centimeters'
    )
    weight_goal = models.FloatField(
        validators=[
            MinValueValidator(20, message='Weight goal must be at least 20 kg'),
            MaxValueValidator(300, message='Weight goal must be less than 300 kg')
        ],
        null=True,
        blank=True,
        help_text='Target weight in kilograms'
    )
    class Mood(models.TextChoices):
        EXCELLENT = 'EXCELLENT', 'Excellent'
        GOOD = 'GOOD', 'Good'
        NEUTRAL = 'NEUTRAL', 'Neutral'
        BAD = 'BAD', 'Bad'
        TERRIBLE = 'TERRIBLE', 'Terrible'

    mood = models.CharField(
        max_length=20,
        choices=Mood.choices,
        help_text='Select your mood for the day'
    )
    mood_correlation = models.FloatField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(-1.0, message='Correlation must be between -1 and 1'),
            MaxValueValidator(1.0, message='Correlation must be between -1 and 1')
        ],
        help_text='Correlation with other health metrics'
    )
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_records'
    )
    last_modified_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='modified_records'
    )
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = [
            ("can_view_own_records", "Can view own records"),
            ("can_edit_own_records", "Can edit own records"),
            ("can_delete_own_records", "Can delete own records"),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.date}"

    def calculate_bmi(self):
        if self.weight and self.height:
            height_in_meters = self.height / 100
            return round(self.weight / (height_in_meters ** 2), 1)
        return None

    def get_bmi_category(self):
        bmi = self.calculate_bmi()
        if bmi is None:
            return None
        if bmi < 18.5:
            return 'Underweight'
        elif bmi < 25:
            return 'Normal weight'
        elif bmi < 30:
            return 'Overweight'
        else:
            return 'Obese'

    def get_weight_progress(self):
        if self.weight and self.weight_goal:
            return round(((self.weight_goal - self.weight) / self.weight) * 100, 1)
        return None

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_record = None
        if not is_new:
            old_record = HealthRecord.objects.get(pk=self.pk)

        super().save(*args, **kwargs)

        if self.weight is not None:
            if self.weight_goal:
                Notification.create_weight_goal_notification(
                    self.user,
                    self.weight,
                    self.weight_goal
                )

            if not is_new and old_record and old_record.weight:
                weight_diff = abs(self.weight - old_record.weight)
                if weight_diff >= 5:
                    milestone = "lost" if self.weight < old_record.weight else "gained"
                    Notification.create_weight_milestone_notification(
                        self.user,
                        self.weight,
                        f"You've {milestone} 5 kg!"
                    )

    def clean(self):
        super().clean()
        errors = {}

        if self.sleep_hours is None:
            errors['sleep_hours'] = 'Sleep hours is required'
        elif self.sleep_hours < 0 or self.sleep_hours > 24:
            errors['sleep_hours'] = 'Sleep hours must be between 0 and 24'

        if self.water_intake is None:
            errors['water_intake'] = 'Water intake is required'
        elif self.water_intake < 0:
            errors['water_intake'] = 'Water intake cannot be negative'
        elif self.water_intake > 10:
            errors['water_intake'] = 'Please enter a realistic water intake amount'

        if self.weight is not None and self.user.weight_goal:
            Notification.create_weight_goal_notification(
                self.user,
                self.weight,
                self.user.weight_goal
            )

        if self.height is not None:
            if self.height < 100:
                errors['height'] = 'Height must be at least 100 cm'
            elif self.height > 250:
                errors['height'] = 'Height must be less than 250 cm'

        if self.weight_goal is not None:
            if self.weight_goal < 20:
                errors['weight_goal'] = 'Weight goal must be at least 20 kg'
            elif self.weight_goal > 300:
                errors['weight_goal'] = 'Weight goal must be less than 300 kg'

        if errors:
            raise ValidationError(errors)


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        WEIGHT_GOAL = 'WEIGHT_GOAL', 'Weight Goal'
        WEIGHT_MILESTONE = 'WEIGHT_MILESTONE', 'Weight Milestone'
        DAILY_REMINDER = 'DAILY_REMINDER', 'Daily Reminder'
        WEEKLY_SUMMARY = 'WEEKLY_SUMMARY', 'Weekly Summary'

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=NotificationType.choices)
    title = models.CharField(max_length=100)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.type} - {self.created_at}"

    @classmethod
    def create_weight_goal_notification(cls, user, current_weight, goal_weight):
        progress = ((goal_weight - current_weight) / current_weight) * 100
        if progress >= 0:
            message = f"You're {abs(progress):.1f}% away from your goal weight of {goal_weight} kg!"
        else:
            message = f"Congratulations! You've exceeded your goal weight of {goal_weight} kg by {abs(progress):.1f}%!"

        return cls.objects.create(
            user=user,
            type=cls.NotificationType.WEIGHT_GOAL,
            title="Weight Goal Update",
            message=message
        )

    @classmethod
    def create_weight_milestone_notification(cls, user, weight, milestone):
        return cls.objects.create(
            user=user,
            type=cls.NotificationType.WEIGHT_MILESTONE,
            title="Weight Milestone Achieved!",
            message=f"Congratulations! You've reached {weight} kg - {milestone}!"
        )


class FoodRecommendation(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    calories = models.IntegerField(null=True, blank=True)
    # Add more fields as needed

    def __str__(self):
        return self.name


class DailyReminderSetting(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='reminder_setting')
    reminder_time = models.TimeField()
    send_email = models.BooleanField(default=False)
    send_in_app = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.reminder_time} (Email: {self.send_email}, In-app: {self.send_in_app})"