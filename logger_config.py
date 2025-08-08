"""
Logging configuration for the Racking PM Automation system.
"""

import logging
import logging.handlers
import os
from pathlib import Path

def setup_logger(name: str = "racking_automation", log_file: str = "racking_automation.log") -> logging.Logger:
    """Set up and configure logger."""
    
    # Create logger
    logger = logging.getLogger(name)
    
    # Don't add handlers if they already exist
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Full path to log file
    log_path = log_dir / log_file
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_path,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(detailed_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # Error file handler (errors only)
    error_log_path = log_dir / "errors.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_path,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.addHandler(error_handler)
    
    # Prevent logging from propagating to the root logger
    logger.propagate = False
    
    return logger

def get_logger(name: str = "racking_automation") -> logging.Logger:
    """Get an existing logger instance."""
    return logging.getLogger(name)

def set_log_level(level: str):
    """Set the logging level for all handlers."""
    logger = get_logger()
    
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    log_level = level_map.get(level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Update all handlers
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.handlers.RotatingFileHandler):
            # Console handler - keep it at INFO or higher
            handler.setLevel(max(log_level, logging.INFO))
        elif 'error' in str(handler.baseFilename).lower():
            # Error handler - keep at ERROR
            handler.setLevel(logging.ERROR)
        else:
            # File handler
            handler.setLevel(log_level)

def log_exception(logger: logging.Logger, message: str):
    """Log an exception with full stack trace."""
    import traceback
    logger.error(f"{message}\n{traceback.format_exc()}")

def create_audit_logger(name: str = "audit") -> logging.Logger:
    """Create a separate audit logger for tracking user actions."""
    audit_logger = logging.getLogger(name)
    
    if audit_logger.handlers:
        return audit_logger
    
    audit_logger.setLevel(logging.INFO)
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Audit log file
    audit_path = log_dir / "audit.log"
    
    # Audit formatter
    audit_formatter = logging.Formatter(
        '%(asctime)s - AUDIT - %(message)s'
    )
    
    # Audit file handler
    audit_handler = logging.handlers.RotatingFileHandler(
        audit_path,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=10
    )
    audit_handler.setLevel(logging.INFO)
    audit_handler.setFormatter(audit_formatter)
    
    audit_logger.addHandler(audit_handler)
    audit_logger.propagate = False
    
    return audit_logger
