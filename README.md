# Health Tracker Project

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-4.2-blue.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A modern Django-based health tracking application that enables users to monitor and visualize their health metrics with an intuitive dashboard and comprehensive analytics.

## 📋 Table of Contents

- [Features](#-features)
- [Screenshots](#-screenshots)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [Support](#-support)
- [License](#-license)

## ✨ Features

### 🎯 Core Features
- **Health Record Tracking**: Log daily sleep hours, water intake, weight, and mood
- **BMI Calculation**: Automatic BMI calculation based on weight and height
- **Mood Tracking**: Track daily mood with predefined options (Excellent, Good, Neutral, Bad, Terrible)
- **User Profiles**: Manage personal details (age, gender, weight goals, sleep goals, water goals)
- **Modern Dashboard**: Responsive UI with Bootstrap and interactive charts
- **Data Visualization**: Weight, sleep, water intake, and mood trend charts
- **Mobile-Friendly**: Fully responsive design for all devices

### 📊 Advanced Features
- **Data Export**: Export health records as CSV
- **PDF Reports**: Generate PDF summaries of health data
- **Daily Reminders**: Automated reminder system with customizable settings
- **Notifications**: In-app notification system for health milestones
- **Goal Tracking**: Set and monitor progress towards weight, sleep, and water intake goals
- **Weekly & Monthly Analytics**: View weekly/monthly averages, streaks, and best/worst days for sleep and water intake (visible on dashboard if you have recent data)

### 🔒 Security Features
- Password validation and strength requirements
- CSRF protection
- XSS prevention
- Secure session management
- User authentication

## 📸 Screenshots

*[Add screenshots of your application here]*

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- SQLite (default) or PostgreSQL (production)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/health-tracker.git
   cd health-tracker
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   .\venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   copy .env.example .env
   # Edit .env with your configuration
   ```

5. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Frontend: http://localhost:8000
   - Admin panel: http://localhost:8000/admin
   - Food Recommendations: http://localhost:8000/food-recommendations/ (also available in the navigation bar)

## 💻 Usage

### Basic Usage

1. **Register/Login**: Create an account or log in to your existing account
2. **Add Health Records**: Use the dashboard to add new health records with sleep, water, weight, and mood data
3. **View Dashboard**: Monitor your health trends and analytics with interactive charts and advanced analytics
4. **Export Data**: Download your health data as CSV or generate PDF reports
5. **Manage Profile**: Update your personal information and set health goals
6. **Set Reminders**: Configure daily reminder settings
7. **View Food Recommendations**: Click the "Food Recommendations" link in the navigation bar

### Health Metrics Tracked

- **Sleep Hours**: Track daily sleep duration (0-24 hours)
- **Water Intake**: Monitor daily water consumption in liters
- **Weight**: Log weight in kilograms with BMI calculation
- **Mood**: Record daily mood from predefined options
- **Goals**: Set targets for weight, sleep, and water intake

### Database Configuration

**SQLite (Default)**
- Used by default for development
- No additional setup required

**PostgreSQL (Production)**
```bash
pip install psycopg2-binary
```
Update `DATABASES` in `health_project/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

After changing databases, run:
```bash
python manage.py makemigrations
python manage.py migrate
```

## 📁 Project Structure

```
health_project/
├── health_project/                 # Project configuration
│   ├── settings.py               # Django settings
│   ├── urls.py                   # URL routing
│   ├── wsgi.py                   # WSGI config
│   └── asgi.py                   # ASGI config
├── tracker/                       # Main application
│   ├── models.py                 # Database models
│   ├── views.py                  # Business logic
│   ├── forms.py                  # Form handling
│   ├── charts.py                 # Data visualization
│   ├── decorators.py             # Custom decorators
│   ├── admin.py                  # Admin interface
│   ├── backup.py                 # Backup functionality
│   ├── export.py                 # Data export
│   ├── utils.py                  # Utility functions
│   ├── static/                   # Static files
│   │   ├── css/
│   │   └── js/
│   ├── templates/                # HTML templates
│   │   └── tracker/
│   │       ├── dashboard.html    # Main dashboard
│   │       ├── add_health_record.html
│   │       ├── profile.html
│   │       ├── notifications.html
│   │       ├── food_recommendations.html
│   │       └── ...
│   └── management/               # Custom commands
│       └── commands/
│           ├── create_backup.py
│           └── send_daily_reminders.py
├── staticfiles/                   # Collected static files
├── backups/                       # Backup files
├── logs/                          # Application logs
├── manage.py                      # Django management script
├── requirements.txt              # Python dependencies
├── gunicorn_config.py           # Production server config
├── start_server.bat             # Windows startup script
├── start_server.sh              # Linux/Mac startup script
└── README.md                     # Project documentation
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Production Settings

For production deployment, update `settings.py`:
- Set `DEBUG=False`
- Configure proper `SECRET_KEY`
- Set up proper `ALLOWED_HOSTS`
- Configure static file serving
- Set up database connections

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test tracker

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 🚀 Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn health_project.wsgi:application
```

### Using Windows Task Scheduler

The project includes scripts for automated backups:
- `backup_scheduler.bat`: Windows backup scheduler
- `create_backup_task.ps1`: PowerShell backup task creation

### Daily Reminders

Set up automated daily reminders:
```bash
# Add to Windows Task Scheduler or cron
python manage.py send_daily_reminders
```

## 🔧 Troubleshooting

### Common Issues

**Missing columns/tables after model changes**
```bash
python manage.py makemigrations
python manage.py migrate
```

**Migration dependency errors**
1. Delete migration files in `tracker/migrations/` (except `__init__.py`)
2. Re-run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

**Database out of sync**
```bash
python manage.py flush  # Development only
```

**Static files not loading**
```bash
python manage.py collectstatic
```

### Getting Help

- Check the [Django documentation](https://docs.djangoproject.com/)
- Review [Common Django Errors and Fixes](https://medium.com/@kanithkar_baskaran/13-django-error-with-solution-775e247c25be)
- Open an issue on GitHub

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting

## 📞 Support

### Getting Help

- **GitHub Issues**: [Open an issue](https://github.com/yourusername/health-tracker/issues)
- **Email**: support@health-tracker.com

### Community

- **GitHub Discussions**: Share ideas and ask questions
- **Discord Channel**: Real-time chat and support

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔒 Privacy & Security

We prioritize user data privacy and security:

- **Data validation** and sanitization
- **Secure authentication** system
- **Regular security audits** and updates
- **Automated backup system** for data protection
- **Privacy policy** documentation available

## 📊 Monitoring

The application includes monitoring for:

- **User activity** tracking
- **Health metrics** analytics
- **Goal progress** monitoring
- **Notification system** for health milestones

---

**Made with ❤️ by the Health Tracker Team**