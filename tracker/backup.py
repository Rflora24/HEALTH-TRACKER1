import os
import shutil
import datetime
import json
from django.conf import settings
from django.core.management import call_command
from django.utils import timezone
from django.utils.translation import gettext as _
from pathlib import Path

class BackupManager:
    """Manager class for handling database backups."""
    
    def __init__(self, backup_dir=None):
        """
        Initialize the backup manager.
        
        Args:
            backup_dir: Directory to store backups (defaults to settings.BACKUP_DIR)
        """
        self.backup_dir = backup_dir or str(settings.BACKUP_DIR)
        os.makedirs(self.backup_dir, exist_ok=True)
        
    def create_backup(self):
        """
        Create a full database backup.
        
        Returns:
            Path to the backup file
        """
        try:
            # Clean up any existing backup directories
            for item in os.listdir(self.backup_dir):
                item_path = Path(self.backup_dir) / item
                if item_path.is_dir() and item.startswith('backup_'):
                    shutil.rmtree(str(item_path))
            
            # Create timestamped backup directory
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            backup_path = Path(self.backup_dir) / f'backup_{timestamp}'
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Dump database
            db_backup_path = backup_path / 'database.json'
            call_command('dumpdata', 'tracker', indent=2, output=str(db_backup_path))
            
            # Copy media files
            media_backup_path = backup_path / 'media'
            if os.path.exists(settings.MEDIA_ROOT):
                # Copy media files, excluding any backup directories
                shutil.copytree(
                    settings.MEDIA_ROOT,
                    str(media_backup_path),
                    ignore=shutil.ignore_patterns('backups')
                )
            
            # Create backup info file
            info = {
                'timestamp': timestamp,
                'backup_type': 'full',
                'database_size': os.path.getsize(str(db_backup_path)),
                'media_count': len(os.listdir(str(media_backup_path))) if media_backup_path.exists() else 0
            }
            
            with open(backup_path / 'backup_info.json', 'w') as f:
                json.dump(info, f, indent=2)
            
            # Create backup archive
            archive_path = Path(self.backup_dir) / f'health_backup_{timestamp}.tar.gz'
            
            # Create archive directly from backup directory
            shutil.make_archive(
                str(archive_path).replace('.tar.gz', ''),
                'gztar',
                str(backup_path),
                '.'
            )
            
            # Clean up backup directory
            shutil.rmtree(str(backup_path))
            
            # Clean up old backup archives if we have too many
            backups = self.list_backups()
            if len(backups) > settings.MAX_BACKUPS:
                # Remove the oldest backup
                oldest_backup = backups[-1]
                os.remove(os.path.join(self.backup_dir, oldest_backup['filename']))
            
            return str(archive_path)
            
        except Exception as e:
            error_msg = f"Backup failed: {str(e)}"
            from django.core.exceptions import ValidationError
            raise ValidationError(error_msg)
            
    def list_backups(self):
        """List all available backups."""
        backups = []
        for filename in os.listdir(self.backup_dir):
            if filename.endswith('.tar.gz'):
                backups.append({
                    'filename': filename,
                    'timestamp': filename.split('_')[2].replace('.tar.gz', ''),
                    'size': os.path.getsize(os.path.join(self.backup_dir, filename))
                })
        return sorted(backups, key=lambda x: x['timestamp'], reverse=True)
        
    def restore_backup(self, backup_file):
        """
        Restore from a backup file.
        
        Args:
            backup_file: Path to the backup file
        """
        try:
            # Extract backup
            extract_dir = Path(self.backup_dir) / 'restore_temp'
            extract_dir.mkdir(parents=True, exist_ok=True)
            
            shutil.unpack_archive(backup_file, str(extract_dir))
            
            # Load database
            db_backup_path = extract_dir / 'database.json'
            if db_backup_path.exists():
                call_command('loaddata', str(db_backup_path))
            
            # Restore media files
            media_backup_path = extract_dir / 'media'
            if media_backup_path.exists():
                if os.path.exists(settings.MEDIA_ROOT):
                    shutil.rmtree(settings.MEDIA_ROOT)
                shutil.copytree(str(media_backup_path), settings.MEDIA_ROOT)
            
            # Clean up
            shutil.rmtree(str(extract_dir))
            
        except Exception as e:
            error_msg = f"Restore failed: {str(e)}"
            from django.core.exceptions import ValidationError
            raise ValidationError(error_msg)
