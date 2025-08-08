"""
Configuration management for the Racking PM Automation system.
"""

import os
import configparser
from pathlib import Path
from typing import Dict, Any, Optional

class Config:
    """Configuration manager for the application."""
    
    def __init__(self, config_file: str = "settings.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load_config()
        
        # Default name to email mappings
        self.pm_emails = {
            "Aaron Cendejas": "aaron@intralog.io",
            "Mark Westover": "mark@intralog.io", 
            "Indigo Allen": "indigo@intralog.io"
        }
        
        self.drafter_emails = {
            "Vanya Andonova": "vanya@intralog.io",
            "Aaron Cendejas": "aaron@intralog.io",
            "Michael Schulte": "michael@intralog.io"
        }
    
    def load_config(self):
        """Load configuration from file."""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration file."""
        # File monitoring settings
        self.config['FileMonitoring'] = {
            'watch_folder': r'C:\Users\*\World Class Integration\Projects - Documents',
            'file_extensions': 'dwg,pdf',
            'polling_interval': '5'
        }
        
        # Odoo settings
        self.config['Odoo'] = {
            'url': 'https://intralog.odoo.com/odoo',
            'username': '',
            'password': '',
            'default_tags': 'Auto-Intake'
        }
        
        # SharePoint settings
        self.config['SharePoint'] = {
            'site_id': '',
            'drive_id': '',
            'tenant_id': '',
            'client_id': '',
            'client_secret': '',
            'base_folder': 'Projects - Documents'
        }
        
        # Email settings
        self.config['Email'] = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': '587',
            'sender_email': 'agent@intralog.io',
            'sender_password': '',
            'use_tls': 'true'
        }
        
        # Seizmic settings
        self.config['Seizmic'] = {
            'portal_url': 'https://portal.seizmicinc.com/',
            'username': '',
            'password': '',
            'enabled': 'false'
        }
        
        # Logging settings
        self.config['Logging'] = {
            'log_level': 'INFO',
            'log_file': 'racking_automation.log',
            'max_log_size': '10485760',  # 10MB
            'backup_count': '5'
        }
        
        self.save_config()
    
    def save_config(self):
        """Save configuration to file."""
        with open(self.config_file, 'w') as f:
            self.config.write(f)
    
    def get(self, section: str, key: str, fallback: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(section, key, fallback=fallback)
    
    def set(self, section: str, key: str, value: str):
        """Set configuration value."""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)
    
    def get_watch_folder(self) -> str:
        """Get the folder to watch for files."""
        folder = self.get('FileMonitoring', 'watch_folder')
        # Expand wildcard in path
        if '*' in folder:
            import glob
            matching_paths = glob.glob(folder)
            if matching_paths:
                return matching_paths[0]
        return folder
    
    def get_file_extensions(self) -> list:
        """Get list of file extensions to monitor."""
        extensions = self.get('FileMonitoring', 'file_extensions', 'dwg,pdf')
        return [ext.strip().lower() for ext in extensions.split(',')]
    
    def get_polling_interval(self) -> int:
        """Get file monitoring polling interval in seconds."""
        return int(self.get('FileMonitoring', 'polling_interval', '5'))
    
    def get_odoo_credentials(self) -> Dict[str, str]:
        """Get Odoo login credentials."""
        return {
            'url': self.get('Odoo', 'url'),
            'username': self.get('Odoo', 'username'),
            'password': self.get('Odoo', 'password')
        }
    
    def get_sharepoint_credentials(self) -> Dict[str, str]:
        """Get SharePoint credentials."""
        return {
            'site_id': self.get('SharePoint', 'site_id'),
            'drive_id': self.get('SharePoint', 'drive_id'),
            'tenant_id': self.get('SharePoint', 'tenant_id'),
            'client_id': self.get('SharePoint', 'client_id'),
            'client_secret': self.get('SharePoint', 'client_secret')
        }
    
    def get_email_credentials(self) -> Dict[str, str]:
        """Get email credentials."""
        return {
            'smtp_server': self.get('Email', 'smtp_server'),
            'smtp_port': int(self.get('Email', 'smtp_port', '587')),
            'sender_email': self.get('Email', 'sender_email'),
            'sender_password': self.get('Email', 'sender_password'),
            'use_tls': self.get('Email', 'use_tls', 'true').lower() == 'true'
        }
    
    def get_seizmic_credentials(self) -> Dict[str, str]:
        """Get Seizmic portal credentials."""
        return {
            'portal_url': self.get('Seizmic', 'portal_url'),
            'username': self.get('Seizmic', 'username'),
            'password': self.get('Seizmic', 'password'),
            'enabled': self.get('Seizmic', 'enabled', 'false').lower() == 'true'
        }
    
    def get_pm_email(self, name: str) -> Optional[str]:
        """Get project manager email by name."""
        return self.pm_emails.get(name)
    
    def get_drafter_email(self, name: str) -> Optional[str]:
        """Get drafter email by name.""" 
        return self.drafter_emails.get(name)
    
    def validate_settings(self) -> bool:
        """Validate that required settings are configured."""
        required_settings = [
            ('Odoo', 'username'),
            ('Odoo', 'password'),
            ('Email', 'sender_email'),
            ('Email', 'sender_password')
        ]
        
        for section, key in required_settings:
            value = self.get(section, key)
            if not value or value.strip() == '':
                return False
        
        # Check if watch folder exists
        watch_folder = self.get_watch_folder()
        if not os.path.exists(watch_folder):
            return False
            
        return True
