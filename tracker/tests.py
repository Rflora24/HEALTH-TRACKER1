from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import HealthRecord, CustomUser
from datetime import datetime, timedelta
import base64

@override_settings(
    STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage',
    DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage'
)
class HealthTrackerTests(TestCase):
    def setUp(self):
        # Create test user with PATIENT role
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            role=CustomUser.Role.PATIENT,
            is_verified=True
        )
        
        # Create test records with all required fields
        self.record1 = HealthRecord.objects.create(
            user=self.user,
            sleep_hours=8,
            water_intake=2.5,
            mood='happy',
            date=datetime.now().date(),
            created_by=self.user,
            last_modified_by=self.user
        )
        self.record2 = HealthRecord.objects.create(
            user=self.user,
            sleep_hours=6,
            water_intake=1.5,
            mood='neutral',
            date=(datetime.now() - timedelta(days=1)).date(),
            created_by=self.user,
            last_modified_by=self.user
        )

    def test_login_required(self):
        """Test that login is required for protected views"""
        # Test dashboard access
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))

        # Test add health record access
        response = self.client.get(reverse('add_health_record'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))

    def test_login_success(self):
        """Test successful login"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'TestPass123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_add_health_record(self):
        """Test adding a health record"""
        # Login first
        self.client.login(username='testuser', password='TestPass123!')
        
        # Add record
        data = {
            'sleep_hours': 7,
            'water_intake': 2.0,
            'mood': 'happy'
        }
        response = self.client.post(reverse('add_health_record'), data)
        self.assertEqual(response.status_code, 302)
        
        # Verify record was created
        record = HealthRecord.objects.filter(
            user=self.user,
            sleep_hours=7,
            water_intake=2.0,
            mood='happy',
            created_by=self.user,
            last_modified_by=self.user
        ).first()
        self.assertIsNotNone(record)

    def test_dashboard_view(self):
        """Test dashboard view"""
        # Login first
        self.client.login(username='testuser', password='TestPass123!')
        
        # Access dashboard
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tracker/dashboard.html')
        
        # Check context data
        self.assertTrue('records' in response.context)
        self.assertEqual(len(response.context['records']), 2)
        
        # Check if chart sections exist
        self.assertContains(response, '<div class="card">')
        self.assertContains(response, 'Sleep Hours')
        self.assertContains(response, 'Water Intake')
        self.assertContains(response, 'Mood Tracking')

    def test_form_validation(self):
        """Test form validation"""
        self.client.login(username='testuser', password='TestPass123!')
        
        # Test invalid sleep hours
        data = {
            'sleep_hours': 25,
            'water_intake': 2.0,
            'mood': 'happy'
        }
        response = self.client.post(reverse('add_health_record'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sleep hours must be between 0 and 24')
        
        # Test invalid water intake
        data = {
            'sleep_hours': 8,
            'water_intake': -1,
            'mood': 'happy'
        }
        response = self.client.post(reverse('add_health_record'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Water intake cannot be negative')

    def test_logout(self):
        """Test logout functionality"""
        # Login first
        self.client.login(username='testuser', password='TestPass123!')
        
        # Test logout
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse('_auth_user_id' in self.client.session)
        
        # Verify can't access protected views after logout
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/login/'))

    def test_health_record_model_validation(self):
        """Test health record model validation"""
        # Test invalid sleep hours
        record = HealthRecord(
            user=self.user,
            sleep_hours=25,
            water_intake=2.0,
            mood='happy',
            created_by=self.user,
            last_modified_by=self.user
        )
        with self.assertRaises(ValidationError):
            record.full_clean()

        # Test invalid water intake
        record = HealthRecord(
            user=self.user,
            sleep_hours=8,
            water_intake=-1,
            mood='happy',
            created_by=self.user,
            last_modified_by=self.user
        )
        with self.assertRaises(ValidationError):
            record.full_clean()

    def test_role_based_access(self):
        """Test role-based access control"""
        # Create a doctor user
        doctor = get_user_model().objects.create_user(
            username='doctor',
            email='doctor@example.com',
            password='DoctorPass123!',
            role=CustomUser.Role.DOCTOR,
            is_verified=True
        )
        
        # Login as doctor
        self.client.login(username='doctor', password='DoctorPass123!')
        
        # Doctor should be able to view patient records
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('records' in response.context)
