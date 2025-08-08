"""
Utility functions for the Racking PM Automation system.
"""

import os
import re
import shutil
import time
import functools
from pathlib import Path
from typing import Any, Callable, Optional

from logger_config import setup_logger

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe use in file systems."""
    # Remove or replace illegal characters
    illegal_chars = r'[<>:"/\\|?*]'
    filename = re.sub(illegal_chars, '_', filename)
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    
    # Handle empty filename
    if not filename:
        filename = "unnamed"
    
    return filename

def sanitize_text(text: str) -> str:
    """Sanitize text for safe use in forms and databases."""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    return text

def create_backup(file_path: str, backup_dir: str = None) -> Optional[str]:
    """Create a backup copy of a file."""
    try:
        logger = setup_logger()
        
        if not os.path.exists(file_path):
            logger.error(f"Source file does not exist: {file_path}")
            return None
        
        # Determine backup directory
        if backup_dir is None:
            backup_dir = os.path.join(os.path.dirname(file_path), 'backups')
        
        # Create backup directory if it doesn't exist
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(file_path)
        name, ext = os.path.splitext(filename)
        backup_filename = f"{name}_{timestamp}{ext}"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Copy file
        shutil.copy2(file_path, backup_path)
        
        logger.info(f"Created backup: {backup_path}")
        return backup_path
        
    except Exception as e:
        logger = setup_logger()
        logger.error(f"Error creating backup: {str(e)}")
        return None

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry function calls on failure."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger = setup_logger()
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. Retrying in {delay} seconds...")
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_retries} attempts failed for {func.__name__}: {str(e)}")
                        raise
        return wrapper
    return decorator

def ensure_directory_exists(directory_path: str) -> bool:
    """Ensure a directory exists, creating it if necessary."""
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        logger = setup_logger()
        logger.error(f"Error creating directory {directory_path}: {str(e)}")
        return False

def safe_file_move(src: str, dst: str) -> bool:
    """Safely move a file with error handling."""
    try:
        logger = setup_logger()
        
        if not os.path.exists(src):
            logger.error(f"Source file does not exist: {src}")
            return False
        
        # Ensure destination directory exists
        dst_dir = os.path.dirname(dst)
        if not ensure_directory_exists(dst_dir):
            return False
        
        # If destination exists, create a unique name
        if os.path.exists(dst):
            name, ext = os.path.splitext(dst)
            counter = 1
            while os.path.exists(f"{name}_{counter}{ext}"):
                counter += 1
            dst = f"{name}_{counter}{ext}"
        
        # Move file
        shutil.move(src, dst)
        logger.info(f"Moved file: {src} -> {dst}")
        return True
        
    except Exception as e:
        logger = setup_logger()
        logger.error(f"Error moving file {src} to {dst}: {str(e)}")
        return False

def get_file_stem_pairs(directory: str, extensions: list) -> list:
    """Find file pairs with matching stems but different extensions."""
    try:
        file_dict = {}
        
        # Scan directory for files
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_obj = Path(file_path)
                
                # Check if extension is in our list
                ext = file_obj.suffix.lower().lstrip('.')
                if ext in [e.lower() for e in extensions]:
                    stem = file_obj.stem.lower()
                    
                    if stem not in file_dict:
                        file_dict[stem] = {}
                    
                    file_dict[stem][ext] = file_path
        
        # Find pairs
        pairs = []
        for stem, files in file_dict.items():
            if len(files) >= 2:
                # We have multiple files with the same stem
                pairs.append(files)
        
        return pairs
        
    except Exception as e:
        logger = setup_logger()
        logger.error(f"Error finding file pairs: {str(e)}")
        return []

def validate_file_path(file_path: str) -> bool:
    """Validate that a file path is safe and accessible."""
    try:
        # Check if path exists
        if not os.path.exists(file_path):
            return False
        
        # Check if it's a file (not directory)
        if not os.path.isfile(file_path):
            return False
        
        # Check if file is readable
        if not os.access(file_path, os.R_OK):
            return False
        
        # Check for suspicious paths
        normalized_path = os.path.normpath(file_path)
        if '..' in normalized_path:
            return False
        
        return True
        
    except Exception:
        return False

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def get_file_info(file_path: str) -> dict:
    """Get comprehensive file information."""
    try:
        if not os.path.exists(file_path):
            return {}
        
        stat = os.stat(file_path)
        
        return {
            'path': file_path,
            'name': os.path.basename(file_path),
            'size': stat.st_size,
            'size_formatted': format_file_size(stat.st_size),
            'modified': time.ctime(stat.st_mtime),
            'created': time.ctime(stat.st_ctime),
            'extension': os.path.splitext(file_path)[1].lower(),
            'is_readable': os.access(file_path, os.R_OK),
            'is_writable': os.access(file_path, os.W_OK)
        }
        
    except Exception as e:
        logger = setup_logger()
        logger.error(f"Error getting file info: {str(e)}")
        return {}

def cleanup_temp_files(temp_dir: str, max_age_hours: int = 24):
    """Clean up temporary files older than specified age."""
    try:
        logger = setup_logger()
        
        if not os.path.exists(temp_dir):
            return
        
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                
                try:
                    file_age = current_time - os.path.getmtime(file_path)
                    
                    if file_age > max_age_seconds:
                        os.remove(file_path)
                        logger.info(f"Cleaned up temp file: {file_path}")
                        
                except Exception as e:
                    logger.warning(f"Could not clean up file {file_path}: {str(e)}")
        
    except Exception as e:
        logger = setup_logger()
        logger.error(f"Error during temp file cleanup: {str(e)}")
