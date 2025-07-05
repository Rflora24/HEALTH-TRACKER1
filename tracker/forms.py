from django import forms
from .models import HealthRecord, CustomUser, DailyReminderSetting
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import MinValueValidator, MaxValueValidator

class HealthRecordForm(forms.ModelForm):
    class Meta:
        model = HealthRecord
        fields = ['sleep_hours', 'water_intake', 'mood', 'weight']
        widgets = {
            'sleep_hours': forms.NumberInput(attrs={
                'step': '0.5',
                'min': '0',
                'max': '24',
                'class': 'form-control',
                'placeholder': 'Enter hours of sleep (0-24)'
            }),
            'water_intake': forms.NumberInput(attrs={
                'step': '0.1',
                'min': '0',
                'class': 'form-control',
                'placeholder': 'Enter water intake in liters'
            }),
            'weight': forms.NumberInput(attrs={
                'step': '0.1',
                'min': '20',
                'max': '300',
                'class': 'form-control',
                'placeholder': 'Enter weight in kilograms'
            }),
            'mood': forms.Select(attrs={
                'class': 'form-select',
            }),
        }
        labels = {
            'sleep_hours': 'Sleep Hours',
            'water_intake': 'Water Intake (liters)',
            'weight': 'Weight (kg)',
            'mood': 'How are you feeling today?',
        }
        help_texts = {
            'sleep_hours': 'Recommended: 7-9 hours',
            'water_intake': 'Recommended: 2-3 liters (8-12 glasses)',
            'weight': 'Enter your current weight in kilograms',
            'mood': 'Select your current mood',
        }

    def clean_sleep_hours(self):
        sleep_hours = self.cleaned_data.get('sleep_hours')
        if sleep_hours < 0 or sleep_hours > 24:
            raise forms.ValidationError('Sleep hours must be between 0 and 24')
        return sleep_hours

    def clean_water_intake(self):
        water_intake = self.cleaned_data.get('water_intake')
        if water_intake < 0:
            raise forms.ValidationError('Water intake cannot be negative')
        if water_intake > 10:
            raise forms.ValidationError('Please enter a realistic water intake amount')
        return water_intake

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, max_length=30)
    last_name = forms.CharField(required=True, max_length=30)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'age', 'gender', 'weight_goal', 'sleep_goal', 'water_goal']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age', 'min': 1, 'max': 120}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'weight_goal': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Target weight in kg', 'step': '0.1', 'min': 20, 'max': 300}),
            'sleep_goal': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Target sleep hours', 'step': '0.5', 'min': 4, 'max': 12}),
            'water_goal': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Target water intake in liters', 'step': '0.1', 'min': 1, 'max': 10}),
        }
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email',
            'age': 'Age',
            'gender': 'Gender',
            'weight_goal': 'Weight Goal (kg)',
            'sleep_goal': 'Sleep Goal (hours)',
            'water_goal': 'Water Goal (liters)',
        }
        help_texts = {
            'email': 'Your email address must be unique.',
            'age': 'Enter your age in years (1-120).',
            'gender': 'Select your gender.',
            'weight_goal': 'Set your target weight in kilograms.',
            'sleep_goal': 'Set your target sleep hours per night (4-12 hours).',
            'water_goal': 'Set your target daily water intake in liters (1-10 liters).',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email

class DailyReminderSettingForm(forms.ModelForm):
    class Meta:
        model = DailyReminderSetting
        fields = ['reminder_time', 'send_email', 'send_in_app']
        widgets = {
            'reminder_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'send_email': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'send_in_app': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'reminder_time': 'Reminder Time',
            'send_email': 'Send Email Reminder',
            'send_in_app': 'Show In-App Notification',
        }
