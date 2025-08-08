"""
Secure credential management for the Racking PM Automation system.
"""

import os
import base64
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pathlib import Path
from typing import Dict, Optional

from logger_config import setup_logger

class CredentialManager:
    """Secure storage and retrieval of credentials."""
    
    def __init__(self, master_password: str = None):
        self.logger = setup_logger()
        self.credentials_file = Path("credentials.enc")
        self.master_password = master_password or os.getenv("MASTER_PASSWORD", "default_key_change_me")
        self._fernet = None
        
    def _get_fernet(self) -> Fernet:
        """Get or create Fernet encryption instance."""
        if self._fernet is None:
            # Derive key from master password
            password = self.master_password.encode()
            salt = b'racking_pm_salt_'  # In production, use a random salt per installation
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            key = base64.urlsafe_b64encode(kdf.derive(password))
            self._fernet = Fernet(key)
            
        return self._fernet
    
    def store_credentials(self, service: str, credentials: Dict[str, str]) -> bool:
        """Store encrypted credentials for a service."""
        try:
            # Load existing credentials
            all_credentials = self._load_all_credentials()
            
            # Update with new credentials
            all_credentials[service] = credentials
            
            # Encrypt and save
            fernet = self._get_fernet()
            data = json.dumps(all_credentials)
            encrypted_data = fernet.encrypt(data.encode())
            
            with open(self.credentials_file, 'wb') as f:
                f.write(encrypted_data)
            
            self.logger.info(f"Stored credentials for service: {service}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error storing credentials for {service}: {str(e)}")
            return False
    
    def get_credentials(self, service: str) -> Optional[Dict[str, str]]:
        """Retrieve decrypted credentials for a service."""
        try:
            all_credentials = self._load_all_credentials()
            return all_credentials.get(service)
            
        except Exception as e:
            self.logger.error(f"Error retrieving credentials for {service}: {str(e)}")
            return None
    
    def remove_credentials(self, service: str) -> bool:
        """Remove credentials for a service."""
        try:
            all_credentials = self._load_all_credentials()
            
            if service in all_credentials:
                del all_credentials[service]
                
                # Save updated credentials
                fernet = self._get_fernet()
                data = json.dumps(all_credentials)
                encrypted_data = fernet.encrypt(data.encode())
                
                with open(self.credentials_file, 'wb') as f:
                    f.write(encrypted_data)
                
                self.logger.info(f"Removed credentials for service: {service}")
                return True
            else:
                self.logger.warning(f"No credentials found for service: {service}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error removing credentials for {service}: {str(e)}")
            return False
    
    def _load_all_credentials(self) -> Dict[str, Dict[str, str]]:
        """Load and decrypt all credentials."""
        try:
            if not self.credentials_file.exists():
                return {}
            
            with open(self.credentials_file, 'rb') as f:
                encrypted_data = f.read()
            
            fernet = self._get_fernet()
            decrypted_data = fernet.decrypt(encrypted_data)
            
            return json.loads(decrypted_data.decode())
            
        except Exception as e:
            self.logger.warning(f"Could not load credentials file: {str(e)}")
            return {}
    
    def list_services(self) -> list:
        """List all services with stored credentials."""
        try:
            all_credentials = self._load_all_credentials()
            return list(all_credentials.keys())
            
        except Exception as e:
            self.logger.error(f"Error listing services: {str(e)}")
            return []
    
    def verify_master_password(self, password: str) -> bool:
        """Verify the master password by attempting to decrypt credentials."""
        try:
            if not self.credentials_file.exists():
                return True  # No credentials file means any password is valid
            
            # Temporarily set password and try to load
            old_password = self.master_password
            old_fernet = self._fernet
            
            self.master_password = password
            self._fernet = None
            
            try:
                self._load_all_credentials()
                return True
            except:
                return False
            finally:
                # Restore original password
                self.master_password = old_password
                self._fernet = old_fernet
                
        except Exception:
            return False
    
    def change_master_password(self, old_password: str, new_password: str) -> bool:
        """Change the master password."""
        try:
            # Verify old password
            if not self.verify_master_password(old_password):
                self.logger.error("Invalid old master password")
                return False
            
            # Load credentials with old password
            old_master = self.master_password
            self.master_password = old_password
            self._fernet = None
            all_credentials = self._load_all_credentials()
            
            # Save with new password
            self.master_password = new_password
            self._fernet = None
            
            fernet = self._get_fernet()
            data = json.dumps(all_credentials)
            encrypted_data = fernet.encrypt(data.encode())
            
            with open(self.credentials_file, 'wb') as f:
                f.write(encrypted_data)
            
            self.logger.info("Master password changed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error changing master password: {str(e)}")
            return False
    
    def backup_credentials(self, backup_path: str) -> bool:
        """Create an encrypted backup of credentials."""
        try:
            import shutil
            import datetime
            
            if not self.credentials_file.exists():
                self.logger.warning("No credentials file to backup")
                return True
            
            # Create backup filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = Path(backup_path)
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            backup_file = backup_dir / f"credentials_backup_{timestamp}.enc"
            
            # Copy encrypted file
            shutil.copy2(self.credentials_file, backup_file)
            
            self.logger.info(f"Credentials backed up to: {backup_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error backing up credentials: {str(e)}")
            return False
    
    def restore_credentials(self, backup_path: str) -> bool:
        """Restore credentials from backup."""
        try:
            import shutil
            
            backup_file = Path(backup_path)
            if not backup_file.exists():
                self.logger.error(f"Backup file not found: {backup_path}")
                return False
            
            # Create backup of current file
            if self.credentials_file.exists():
                current_backup = f"{self.credentials_file}.bak"
                shutil.copy2(self.credentials_file, current_backup)
            
            # Restore from backup
            shutil.copy2(backup_file, self.credentials_file)
            
            # Verify we can decrypt the restored file
            try:
                self._load_all_credentials()
                self.logger.info(f"Credentials restored from: {backup_path}")
                return True
            except Exception as e:
                # Restore failed, revert if we had a backup
                if self.credentials_file.exists():
                    current_backup = f"{self.credentials_file}.bak"
                    if os.path.exists(current_backup):
                        shutil.copy2(current_backup, self.credentials_file)
                
                self.logger.error(f"Could not decrypt restored credentials: {str(e)}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error restoring credentials: {str(e)}")
            return False
