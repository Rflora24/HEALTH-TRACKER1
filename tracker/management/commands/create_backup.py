from django.core.management.base import BaseCommand
from tracker.backup import BackupManager
import logging

class Command(BaseCommand):
    help = 'Create a backup of the database and media files'
    
    def handle(self, *args, **options):
        backup_manager = BackupManager()
        try:
            backup_path = backup_manager.create_backup()
            self.stdout.write(self.style.SUCCESS(f'Successfully created backup: {backup_path}'))
            logging.info(f'Backup created successfully: {backup_path}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Backup failed: {str(e)}'))
            logging.error(f'Backup failed: {str(e)}')
