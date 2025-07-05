#!/usr/bin/env python
import os
import sys
import django
from django.core.management import execute_from_command_line

def run_tests():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_project.test_settings')
    django.setup()
    
    # Run the tests with coverage
    try:
        import coverage
        cov = coverage.Coverage()
        cov.start()
    except ImportError:
        print("Coverage not installed. Running tests without coverage.")
        cov = None
    
    # Run the tests
    execute_from_command_line(['manage.py', 'test', 'tracker', '--keepdb'])
    
    if cov:
        cov.stop()
        cov.save()
        
        # Print coverage report
        print("\nCoverage Report:")
        cov.report()
        
        # Generate HTML report
        cov.html_report(directory='coverage_html')
        print("\nHTML coverage report generated in 'coverage_html' directory")

if __name__ == '__main__':
    run_tests() 