@echo off

:: Create and activate virtual environment
python -m venv venv
CALL venv\Scripts\activate.bat

:: Install dependencies
pip install -r requirements.txt

:: Collect static files
python manage.py collectstatic --noinput

:: Migrate database
python manage.py migrate

:: Start server
gunicorn health_project.wsgi:application --config gunicorn_config.py
python manage.py collectstatic --noinput

:: Apply migrations
python manage.py migrate

:: Start Gunicorn server
gunicorn health_project.wsgi:application --config gunicorn.conf.py
