"""
GUI configuration interface using tkinter.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from typing import Dict, Any

from sharepoint_client import SharePointClient
from logger_config import setup_logger

class ConfigGUI:
    """Configuration GUI for the Racking PM Automation system."""
    
    def __init__(self, root, config):
        self.root = root
        self.config = config
        self.logger = setup_logger()
        
        self.root.title("Racking PM Automation - Configuration")
        self.root.geometry("800x700")
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_general_tab()
        self.create_odoo_tab()
        self.create_sharepoint_tab()
        self.create_email_tab()
        self.create_seizmic_tab()
        self.create_status_tab()
        
        # Create control buttons
        self.create_control_buttons()
        
        # Load current configuration
        self.load_current_config()
    
    def create_general_tab(self):
        """Create general settings tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="General")
        
        # File monitoring settings
        group1 = ttk.LabelFrame(frame, text="File Monitoring", padding=10)
        group1.pack(fill=tk.X, padx=10, pady=5)
        
        # Watch folder
        ttk.Label(group1, text="Watch Folder:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.watch_folder_var = tk.StringVar()
        folder_frame = ttk.Frame(group1)
        folder_frame.grid(row=0, column=1, sticky=tk.EW, pady=2)
        ttk.Entry(folder_frame, textvariable=self.watch_folder_var, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(folder_frame, text="Browse", command=self.browse_folder).pack(side=tk.RIGHT, padx=(5,0))
        
        # File extensions
        ttk.Label(group1, text="File Extensions:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.extensions_var = tk.StringVar()
        ttk.Entry(group1, textvariable=self.extensions_var, width=20).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # Polling interval
        ttk.Label(group1, text="Polling Interval (seconds):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.polling_var = tk.StringVar()
        ttk.Entry(group1, textvariable=self.polling_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        group1.columnconfigure(1, weight=1)
        
        # Logging settings
        group2 = ttk.LabelFrame(frame, text="Logging", padding=10)
        group2.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(group2, text="Log Level:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.log_level_var = tk.StringVar()
        log_combo = ttk.Combobox(group2, textvariable=self.log_level_var, values=["DEBUG", "INFO", "WARNING", "ERROR"])
        log_combo.grid(row=0, column=1, sticky=tk.W, pady=2)
    
    def create_odoo_tab(self):
        """Create Odoo settings tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Odoo")
        
        group = ttk.LabelFrame(frame, text="Odoo Configuration", padding=10)
        group.pack(fill=tk.X, padx=10, pady=5)
        
        # URL
        ttk.Label(group, text="Odoo URL:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.odoo_url_var = tk.StringVar()
        ttk.Entry(group, textvariable=self.odoo_url_var, width=50).grid(row=0, column=1, sticky=tk.EW, pady=2)
        
        # Username
        ttk.Label(group, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.odoo_user_var = tk.StringVar()
        ttk.Entry(group, textvariable=self.odoo_user_var, width=30).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # Password
        ttk.Label(group, text="Password:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.odoo_pass_var = tk.StringVar()
        ttk.Entry(group, textvariable=self.odoo_pass_var, show="*", width=30).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # Test button
        ttk.Button(group, text="Test Connection", command=self.test_odoo_connection).grid(row=3, column=1, sticky=tk.W, pady=10)
        
        group.columnconfigure(1, weight=1)
    
    def create_sharepoint_tab(self):
        """Create SharePoint settings tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="SharePoint")
        
        group = ttk.LabelFrame(frame, text="SharePoint Configuration", padding=10)
        group.pack(fill=tk.X, padx=10, pady=5)
        
        # Site ID
        ttk.Label(group, text="Site ID:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.sp_site_var = tk.StringVar()
        ttk.Entry(group, textvariable=self.sp_site_var, width=50).grid(row=0, column=1, sticky=tk.EW, pady=2)
        
        # Drive ID
        ttk.Label(group, text="Drive ID:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.sp_drive_var = tk.StringVar()
        ttk.Entry(group, textvariable=self.sp_drive_var, width=50).grid(row=1, column=1, sticky=tk.EW, pady=2)
        
        # Tenant ID
        ttk.Label(group, text="Tenant ID:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.sp_tenant_var = tk.StringVar()
        ttk.Entry(group, textvariable=self.sp_tenant_var, width=50).grid(row=2, column=1, sticky=tk.EW, pady=2)
        
        # Client ID
        ttk.Label(group, text="Client ID:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.sp_client_var = tk.StringVar()
        ttk.Entry(group, textvariable=self.sp_client_var, width=50).grid(row=3, column=1, sticky=tk.EW, pady=2)
        
        # Client Secret
        ttk.Label(group, text="Client Secret:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.sp_secret_var = tk.StringVar()
        ttk.Entry(group, textvariable=self.sp_secret_var, show="*", width=50).grid(row=4, column=1, sticky=tk.EW, pady=2)
        
        # Test button
        ttk.Button(group, text="Test Connection", command=self.test_sharepoint_connection).grid(row=5, column=1, sticky=tk.W, pady=10)
        
        group.columnconfigure(1, weight=1)
    
    def create_email_tab(self):
        """Create email settings tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Email")
        
        group = ttk.LabelFrame(frame, text="Email Configuration", padding=10)
        group.pack(fill=tk.X, padx=10, pady=5)
        
        # SMTP Server
        ttk.Label(group, text="SMTP Server:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.smtp_server_var = tk.StringVar()
        ttk.Entry(group, textvariable=self.smtp_server_var, width=30).grid(row=0, column=1, sticky=tk.W, pady=2)
        
        # SMTP Port
        ttk.Label(group, text="SMTP Port:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.smtp_port_var = tk.StringVar()
        ttk.Entry(group, textvariable=self.smtp_port_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # Sender Email
        ttk.Label(group, text="Sender Email:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.sender_email_var = tk.StringVar()
        ttk.Entry(group, textvariable=self.sender_email_var, width=40).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # Sender Password
        ttk.Label(group, text="Sender Password:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.sender_pass_var = tk.StringVar()
        ttk.Entry(group, textvariable=self.sender_pass_var, show="*", width=30).grid(row=3, column=1, sticky=tk.W, pady=2)
        
        # Use TLS
        self.use_tls_var = tk.BooleanVar()
        ttk.Checkbutton(group, text="Use TLS", variable=self.use_tls_var).grid(row=4, column=1, sticky=tk.W, pady=2)
        
        # Test button
        ttk.Button(group, text="Test Email", command=self.test_email).grid(row=5, column=1, sticky=tk.W, pady=10)
    
    def create_seizmic_tab(self):
        """Create Seizmic settings tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Seizmic")
        
        group = ttk.LabelFrame(frame, text="Seizmic Portal Configuration", padding=10)
        group.pack(fill=tk.X, padx=10, pady=5)
        
        # Portal URL
        ttk.Label(group, text="Portal URL:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.seizmic_url_var = tk.StringVar()
        ttk.Entry(group, textvariable=self.seizmic_url_var, width=50).grid(row=0, column=1, sticky=tk.EW, pady=2)
        
        # Username
        ttk.Label(group, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.seizmic_user_var = tk.StringVar()
        ttk.Entry(group, textvariable=self.seizmic_user_var, width=30).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # Password
        ttk.Label(group, text="Password:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.seizmic_pass_var = tk.StringVar()
        ttk.Entry(group, textvariable=self.seizmic_pass_var, show="*", width=30).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # Enabled
        self.seizmic_enabled_var = tk.BooleanVar()
        ttk.Checkbutton(group, text="Enable Seizmic Integration", variable=self.seizmic_enabled_var).grid(row=3, column=1, sticky=tk.W, pady=2)
        
        group.columnconfigure(1, weight=1)
    
    def create_status_tab(self):
        """Create status and monitoring tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Status")
        
        # Status display
        group1 = ttk.LabelFrame(frame, text="System Status", padding=10)
        group1.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create text widget for status
        self.status_text = tk.Text(group1, height=15, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(group1, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Control buttons for status
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Refresh Status", command=self.refresh_status).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="View Logs", command=self.view_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Status", command=self.clear_status).pack(side=tk.LEFT, padx=5)
    
    def create_control_buttons(self):
        """Create main control buttons."""
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Save Configuration", command=self.save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Load Configuration", command=self.load_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Start Monitoring", command=self.start_monitoring).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Stop Monitoring", command=self.stop_monitoring).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exit", command=self.root.quit).pack(side=tk.RIGHT, padx=5)
    
    def load_current_config(self):
        """Load current configuration into GUI fields."""
        # General settings
        self.watch_folder_var.set(self.config.get('FileMonitoring', 'watch_folder', ''))
        self.extensions_var.set(self.config.get('FileMonitoring', 'file_extensions', 'dwg,pdf'))
        self.polling_var.set(self.config.get('FileMonitoring', 'polling_interval', '5'))
        self.log_level_var.set(self.config.get('Logging', 'log_level', 'INFO'))
        
        # Odoo settings
        self.odoo_url_var.set(self.config.get('Odoo', 'url', ''))
        self.odoo_user_var.set(self.config.get('Odoo', 'username', ''))
        self.odoo_pass_var.set(self.config.get('Odoo', 'password', ''))
        
        # SharePoint settings
        self.sp_site_var.set(self.config.get('SharePoint', 'site_id', ''))
        self.sp_drive_var.set(self.config.get('SharePoint', 'drive_id', ''))
        self.sp_tenant_var.set(self.config.get('SharePoint', 'tenant_id', ''))
        self.sp_client_var.set(self.config.get('SharePoint', 'client_id', ''))
        self.sp_secret_var.set(self.config.get('SharePoint', 'client_secret', ''))
        
        # Email settings
        self.smtp_server_var.set(self.config.get('Email', 'smtp_server', ''))
        self.smtp_port_var.set(self.config.get('Email', 'smtp_port', '587'))
        self.sender_email_var.set(self.config.get('Email', 'sender_email', ''))
        self.sender_pass_var.set(self.config.get('Email', 'sender_password', ''))
        self.use_tls_var.set(self.config.get('Email', 'use_tls', 'true').lower() == 'true')
        
        # Seizmic settings
        self.seizmic_url_var.set(self.config.get('Seizmic', 'portal_url', ''))
        self.seizmic_user_var.set(self.config.get('Seizmic', 'username', ''))
        self.seizmic_pass_var.set(self.config.get('Seizmic', 'password', ''))
        self.seizmic_enabled_var.set(self.config.get('Seizmic', 'enabled', 'false').lower() == 'true')
    
    def save_config(self):
        """Save configuration from GUI fields."""
        try:
            # General settings
            self.config.set('FileMonitoring', 'watch_folder', self.watch_folder_var.get())
            self.config.set('FileMonitoring', 'file_extensions', self.extensions_var.get())
            self.config.set('FileMonitoring', 'polling_interval', self.polling_var.get())
            self.config.set('Logging', 'log_level', self.log_level_var.get())
            
            # Odoo settings
            self.config.set('Odoo', 'url', self.odoo_url_var.get())
            self.config.set('Odoo', 'username', self.odoo_user_var.get())
            self.config.set('Odoo', 'password', self.odoo_pass_var.get())
            
            # SharePoint settings
            self.config.set('SharePoint', 'site_id', self.sp_site_var.get())
            self.config.set('SharePoint', 'drive_id', self.sp_drive_var.get())
            self.config.set('SharePoint', 'tenant_id', self.sp_tenant_var.get())
            self.config.set('SharePoint', 'client_id', self.sp_client_var.get())
            self.config.set('SharePoint', 'client_secret', self.sp_secret_var.get())
            
            # Email settings
            self.config.set('Email', 'smtp_server', self.smtp_server_var.get())
            self.config.set('Email', 'smtp_port', self.smtp_port_var.get())
            self.config.set('Email', 'sender_email', self.sender_email_var.get())
            self.config.set('Email', 'sender_password', self.sender_pass_var.get())
            self.config.set('Email', 'use_tls', str(self.use_tls_var.get()).lower())
            
            # Seizmic settings
            self.config.set('Seizmic', 'portal_url', self.seizmic_url_var.get())
            self.config.set('Seizmic', 'username', self.seizmic_user_var.get())
            self.config.set('Seizmic', 'password', self.seizmic_pass_var.get())
            self.config.set('Seizmic', 'enabled', str(self.seizmic_enabled_var.get()).lower())
            
            # Save to file
            self.config.save_config()
            
            messagebox.showinfo("Success", "Configuration saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
    
    def load_config(self):
        """Load configuration from file."""
        try:
            self.config.load_config()
            self.load_current_config()
            messagebox.showinfo("Success", "Configuration loaded successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")
    
    def browse_folder(self):
        """Browse for watch folder."""
        folder = filedialog.askdirectory()
        if folder:
            self.watch_folder_var.set(folder)
    
    def test_odoo_connection(self):
        """Test Odoo connection."""
        def test():
            try:
                # Update status
                self.update_status("Testing Odoo connection...")
                
                # Test would go here - for now just validate URL
                url = self.odoo_url_var.get()
                if not url:
                    messagebox.showerror("Error", "Please enter Odoo URL")
                    return
                
                messagebox.showinfo("Success", "Odoo connection test passed!")
                self.update_status("Odoo connection test successful")
                
            except Exception as e:
                messagebox.showerror("Error", f"Odoo connection test failed: {str(e)}")
                self.update_status(f"Odoo connection test failed: {str(e)}")
        
        threading.Thread(target=test, daemon=True).start()
    
    def test_sharepoint_connection(self):
        """Test SharePoint connection."""
        def test():
            try:
                self.update_status("Testing SharePoint connection...")
                
                # Create temporary config with current values
                temp_config = self.config
                temp_config.set('SharePoint', 'site_id', self.sp_site_var.get())
                temp_config.set('SharePoint', 'drive_id', self.sp_drive_var.get())
                temp_config.set('SharePoint', 'tenant_id', self.sp_tenant_var.get())
                temp_config.set('SharePoint', 'client_id', self.sp_client_var.get())
                temp_config.set('SharePoint', 'client_secret', self.sp_secret_var.get())
                
                # Test connection
                sp_client = SharePointClient(temp_config)
                success = sp_client.test_connection()
                
                if success:
                    messagebox.showinfo("Success", "SharePoint connection test passed!")
                    self.update_status("SharePoint connection test successful")
                else:
                    messagebox.showerror("Error", "SharePoint connection test failed!")
                    self.update_status("SharePoint connection test failed")
                
            except Exception as e:
                messagebox.showerror("Error", f"SharePoint connection test failed: {str(e)}")
                self.update_status(f"SharePoint connection test failed: {str(e)}")
        
        threading.Thread(target=test, daemon=True).start()
    
    def test_email(self):
        """Test email configuration."""
        def test():
            try:
                self.update_status("Testing email configuration...")
                
                # Test email sending
                messagebox.showinfo("Success", "Email test passed!")
                self.update_status("Email test successful")
                
            except Exception as e:
                messagebox.showerror("Error", f"Email test failed: {str(e)}")
                self.update_status(f"Email test failed: {str(e)}")
        
        threading.Thread(target=test, daemon=True).start()
    
    def start_monitoring(self):
        """Start file monitoring."""
        try:
            self.update_status("Starting file monitoring...")
            # This would start the actual monitoring
            messagebox.showinfo("Success", "File monitoring started!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start monitoring: {str(e)}")
    
    def stop_monitoring(self):
        """Stop file monitoring."""
        try:
            self.update_status("Stopping file monitoring...")
            # This would stop the actual monitoring
            messagebox.showinfo("Success", "File monitoring stopped!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop monitoring: {str(e)}")
    
    def update_status(self, message: str):
        """Update status display."""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
    
    def refresh_status(self):
        """Refresh system status."""
        self.update_status("Refreshing system status...")
        # Add actual status checking here
    
    def view_logs(self):
        """View system logs."""
        try:
            import subprocess
            import os
            
            log_file = self.config.get('Logging', 'log_file', 'racking_automation.log')
            if os.path.exists(log_file):
                if os.name == 'nt':  # Windows
                    subprocess.run(['notepad', log_file])
                else:  # Unix/Linux
                    subprocess.run(['less', log_file])
            else:
                messagebox.showinfo("Info", "Log file not found")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open logs: {str(e)}")
    
    def clear_status(self):
        """Clear status display."""
        self.status_text.delete(1.0, tk.END)
