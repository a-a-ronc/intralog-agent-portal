"""
File monitoring system for detecting DWG/PDF pairs.
"""

import os
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from pdf_parser import PDFParser
from odoo_automation import OdooAutomation
from sharepoint_client import SharePointClient
from email_handler import EmailHandler
from logger_config import setup_logger
from utils import sanitize_filename, create_backup

class FileProcessor:
    """Processes detected file pairs."""
    
    def __init__(self, config):
        self.config = config
        self.logger = setup_logger()
        self.pdf_parser = PDFParser()
        self.odoo_automation = OdooAutomation(config)
        self.sharepoint_client = SharePointClient(config)
        self.email_handler = EmailHandler(config)
    
    def process_file_pair(self, dwg_file: str, pdf_file: str) -> bool:
        """Process a DWG/PDF file pair."""
        try:
            self.logger.info(f"Processing file pair: {pdf_file}, {dwg_file}")
            
            # Create backup copies
            pdf_backup = create_backup(pdf_file)
            dwg_backup = create_backup(dwg_file)
            
            # Extract metadata from PDF
            metadata = self.pdf_parser.extract_title_block(pdf_file)
            if not metadata:
                self.logger.error(f"Failed to extract metadata from {pdf_file}")
                return False
            
            self.logger.info(f"Extracted metadata: {metadata}")
            
            # Create Odoo opportunity
            opportunity_number = self.odoo_automation.create_opportunity(metadata)
            if not opportunity_number:
                self.logger.error("Failed to create Odoo opportunity")
                return False
            
            self.logger.info(f"Created Odoo opportunity: {opportunity_number}")
            
            # Create SharePoint folder structure
            folder_path = self.sharepoint_client.create_folder_structure(
                metadata, opportunity_number
            )
            if not folder_path:
                self.logger.error("Failed to create SharePoint folder structure")
                return False
            
            self.logger.info(f"Created SharePoint folders at: {folder_path}")
            
            # Move files to SharePoint
            success = self.sharepoint_client.move_files_to_sharepoint(
                pdf_file, dwg_file, folder_path
            )
            if not success:
                self.logger.error("Failed to move files to SharePoint")
                return False
            
            # Send email for Seizmic data collection
            self.email_handler.send_seizmic_data_request(metadata, opportunity_number)
            
            self.logger.info(f"Successfully processed file pair: {pdf_file}, {dwg_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing file pair: {str(e)}")
            return False

class FileMonitorHandler(FileSystemEventHandler):
    """Handles file system events."""
    
    def __init__(self, config):
        self.config = config
        self.logger = setup_logger()
        self.processor = FileProcessor(config)
        self.file_cache = {}  # Track files for pairing
        self.processing_lock = set()  # Prevent duplicate processing
    
    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return
        
        file_path = str(event.src_path)
        self.check_for_file_pair(file_path)
    
    def on_moved(self, event):
        """Handle file move events."""
        if event.is_directory:
            return
        
        file_path = str(event.dest_path)
        self.check_for_file_pair(file_path)
    
    def check_for_file_pair(self, file_path: str):
        """Check if we have a DWG/PDF pair and process if found."""
        try:
            file_path_obj = Path(file_path)
            file_stem = file_path_obj.stem.lower()
            file_ext = file_path_obj.suffix.lower().lstrip('.')
            
            # Only process DWG and PDF files
            if file_ext not in ['dwg', 'pdf']:
                return
            
            # Skip if already processing this stem
            if file_stem in self.processing_lock:
                return
            
            # Store file in cache
            if file_stem not in self.file_cache:
                self.file_cache[file_stem] = {}
            
            self.file_cache[file_stem][file_ext] = str(file_path)
            
            # Check if we have both DWG and PDF
            if 'dwg' in self.file_cache[file_stem] and 'pdf' in self.file_cache[file_stem]:
                self.processing_lock.add(file_stem)
                
                try:
                    dwg_file = self.file_cache[file_stem]['dwg']
                    pdf_file = self.file_cache[file_stem]['pdf']
                    
                    # Verify both files exist
                    if os.path.exists(dwg_file) and os.path.exists(pdf_file):
                        # Process in background thread
                        import threading
                        process_thread = threading.Thread(
                            target=self._process_pair_async,
                            args=(dwg_file, pdf_file, file_stem)
                        )
                        process_thread.daemon = True
                        process_thread.start()
                    
                except Exception as e:
                    self.logger.error(f"Error processing file pair {file_stem}: {str(e)}")
                    self.processing_lock.discard(file_stem)
        
        except Exception as e:
            self.logger.error(f"Error checking file pair: {str(e)}")
    
    def _process_pair_async(self, dwg_file: str, pdf_file: str, file_stem: str):
        """Process file pair asynchronously."""
        try:
            success = self.processor.process_file_pair(dwg_file, pdf_file)
            if success:
                self.logger.info(f"Successfully processed pair: {file_stem}")
            else:
                self.logger.error(f"Failed to process pair: {file_stem}")
        
        except Exception as e:
            self.logger.error(f"Error in async processing: {str(e)}")
        
        finally:
            # Remove from processing lock and cache
            self.processing_lock.discard(file_stem)
            if file_stem in self.file_cache:
                del self.file_cache[file_stem]

class FileMonitor:
    """Main file monitoring class."""
    
    def __init__(self, config):
        self.config = config
        self.logger = setup_logger()
        self.observer = None
        self.running = False
    
    def start_watching(self):
        """Start watching the configured folder."""
        try:
            watch_folder = self.config.get_watch_folder()
            
            if not os.path.exists(watch_folder):
                self.logger.error(f"Watch folder does not exist: {watch_folder}")
                return False
            
            self.logger.info(f"Starting file monitoring on: {watch_folder}")
            
            # Set up file system observer
            self.observer = Observer()
            event_handler = FileMonitorHandler(self.config)
            
            self.observer.schedule(
                event_handler,
                watch_folder,
                recursive=True
            )
            
            self.observer.start()
            self.running = True
            
            # Also scan existing files on startup
            self._scan_existing_files(watch_folder, event_handler)
            
            # Keep observer running
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.logger.info("Received keyboard interrupt")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting file monitoring: {str(e)}")
            return False
    
    def stop_watching(self):
        """Stop watching for files."""
        try:
            if self.observer and self.observer.is_alive():
                self.observer.stop()
                self.observer.join()
            
            self.running = False
            self.logger.info("File monitoring stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping file monitoring: {str(e)}")
    
    def _scan_existing_files(self, folder: str, handler: FileMonitorHandler):
        """Scan for existing file pairs on startup."""
        try:
            self.logger.info("Scanning for existing file pairs...")
            
            for root, dirs, files in os.walk(folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    handler.check_for_file_pair(file_path)
            
            self.logger.info("Existing file scan completed")
            
        except Exception as e:
            self.logger.error(f"Error scanning existing files: {str(e)}")
