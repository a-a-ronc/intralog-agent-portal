#!/usr/bin/env python3
"""
Racking PM Automation System
Main entry point for the desktop automation application.
"""

import sys
import os
import threading
import time
import signal
from pathlib import Path

from file_monitor import FileMonitor
from config import Config
from logger_config import setup_logger
from gui_config import ConfigGUI
import tkinter as tk
from tkinter import messagebox

class RackingAutomationApp:
    """Main application class for the Racking PM Automation system."""
    
    def __init__(self):
        self.logger = setup_logger()
        self.config = Config()
        self.file_monitor = None
        self.running = False
        
    def start_monitoring(self):
        """Start the file monitoring system."""
        try:
            # Validate configuration
            if not self.config.validate_settings():
                self.logger.error("Invalid configuration. Please check settings.")
                return False
                
            # Initialize file monitor
            self.file_monitor = FileMonitor(self.config)
            
            # Start monitoring in a separate thread
            monitor_thread = threading.Thread(target=self.file_monitor.start_watching)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            self.running = True
            self.logger.info("Racking PM Automation started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {str(e)}")
            return False
    
    def stop_monitoring(self):
        """Stop the file monitoring system."""
        try:
            if self.file_monitor:
                self.file_monitor.stop_watching()
            self.running = False
            self.logger.info("Racking PM Automation stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping monitoring: {str(e)}")
    
    def show_config_gui(self):
        """Show the configuration GUI."""
        try:
            root = tk.Tk()
            app = ConfigGUI(root, self.config)
            root.mainloop()
            
        except Exception as e:
            self.logger.error(f"Error showing config GUI: {str(e)}")
    
    def run_console_mode(self):
        """Run the application in console mode."""
        self.logger.info("Starting Racking PM Automation in console mode")
        
        if not self.start_monitoring():
            self.logger.error("Failed to start monitoring. Exiting.")
            return
        
        try:
            # Keep the main thread alive
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
        finally:
            self.stop_monitoring()

def signal_handler(signum, frame):
    """Handle system signals for graceful shutdown."""
    print("\nReceived shutdown signal. Stopping application...")
    sys.exit(0)

def main():
    """Main entry point."""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    app = RackingAutomationApp()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--config":
            # Show configuration GUI
            app.show_config_gui()
            return
        elif sys.argv[1] == "--console":
            # Run in console mode
            app.run_console_mode()
            return
        elif sys.argv[1] == "--help":
            print("Racking PM Automation System")
            print("Usage:")
            print("  python main.py --config    Show configuration GUI")
            print("  python main.py --console   Run in console mode")
            print("  python main.py --help      Show this help")
            print("  python main.py             Show configuration GUI (default)")
            return
    
    # Default: show configuration GUI
    app.show_config_gui()

if __name__ == "__main__":
    main()
