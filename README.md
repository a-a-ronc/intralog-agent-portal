# Racking PM Automation System

A comprehensive desktop automation system for project management workflows that monitors DWG/PDF file pairs, extracts metadata, creates Odoo opportunities, manages SharePoint folder structures, and automates email communications.

## Overview

This system automates the complete workflow from file detection to project setup:

1. **File Monitoring**: Watches specified directories for DWG/PDF file pairs
2. **Metadata Extraction**: Parses PDF title blocks to extract project information
3. **Odoo Integration**: Automatically creates opportunities with extracted data
4. **SharePoint Management**: Creates structured folder hierarchies and moves files
5. **Email Automation**: Sends data collection requests and notifications
6. **Seizmic Integration**: Optional portal form submission (when enabled)

## Features

### Core Functionality
- Real-time file system monitoring using Watchdog
- PDF title block parsing with configurable patterns
- Selenium-based Odoo automation for opportunity creation
- Microsoft Graph API integration for SharePoint operations
- SMTP email automation with template system
- Encrypted credential storage with Fernet encryption
- Comprehensive logging with rotation and audit trails

### User Interface
- Desktop GUI configuration using Tkinter
- Tabbed interface for different service configurations
- Real-time status monitoring and log viewing
- Connection testing for all integrated services
- Start/stop controls for monitoring system

### Security Features
- Encrypted credential storage using industry-standard encryption
- Master password protection for credential access
- Secure backup and restore functionality
- Audit logging for all system actions

## System Requirements

### Python Dependencies
- Python 3.8 or higher
- watchdog (file system monitoring)
- pdfplumber (PDF text extraction)
- selenium (web automation)
- msal (Microsoft authentication)
- cryptography (secure credential storage)
- requests (HTTP client)
- tkinter (GUI framework - usually included with Python)

### External Dependencies
- Chrome or Chromium browser (for Selenium automation)
- ChromeDriver (automatically managed by Selenium)

### System Access
- Microsoft 365 tenant with SharePoint access
- Odoo instance with web access
- SMTP server for email sending

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/a-a-ronc/intralog-agent-portal.git
   cd intralog-agent-portal
   ```

2. **Install dependencies**:
   ```bash
   pip install watchdog pdfplumber selenium msal cryptography requests
   ```

3. **Run the configuration GUI**:
   ```bash
   python main.py --config
   ```

## Configuration

### Initial Setup

1. **Launch Configuration Interface**:
   ```bash
   python main.py --config
   ```

2. **Configure File Monitoring** (General tab):
   - Set watch folder path (supports wildcards like `C:\Users\*\World Class Integration\Projects - Documents`)
   - Configure file extensions (default: dwg,pdf)
   - Set polling interval (default: 5 seconds)

3. **Setup Odoo Integration** (Odoo tab):
   - Enter Odoo URL (e.g., `https://intralog.odoo.com/odoo`)
   - Provide username and password
   - Test connection to verify credentials

4. **Configure SharePoint** (SharePoint tab):
   - Enter Site ID and Drive ID for your SharePoint site
   - Provide Tenant ID, Client ID, and Client Secret
   - Test connection to verify permissions

5. **Setup Email** (Email tab):
   - Configure SMTP server details
   - Enter sender email credentials
   - Test email functionality

6. **Optional: Seizmic Integration** (Seizmic tab):
   - Enter portal URL and credentials
   - Enable/disable integration as needed

### SharePoint Setup

To get your SharePoint Site ID and Drive ID:

1. Navigate to your SharePoint site
2. Use Microsoft Graph Explorer or PowerShell to query:
   - Site ID: `GET https://graph.microsoft.com/v1.0/sites/{hostname}:{sitePath}`
   - Drive ID: `GET https://graph.microsoft.com/v1.0/sites/{siteId}/drives`

Required permissions for the Azure app:
- `Sites.Read.All`
- `Files.ReadWrite.All`
- `offline_access`
- `User.Read`

## Usage

### Starting the System

**GUI Mode** (recommended for setup and monitoring):
```bash
python main.py --config
```

**Console Mode** (for production deployment):
```bash
python main.py --console
```

**Help**:
```bash
python main.py --help
```

### Workflow Process

1. **File Detection**: System monitors configured folder for new DWG/PDF pairs
2. **Metadata Extraction**: PDF title block is parsed for:
   - Customer name
   - Facility address
   - Project manager
   - Drafter name
   - Project title/description

3. **Odoo Opportunity Creation**:
   - Logs into Odoo using Selenium
   - Creates new opportunity with extracted data
   - Assigns project manager as salesperson
   - Adds "Auto-Intake" tag
   - Captures opportunity number

4. **SharePoint Folder Structure**:
   ```
   /Projects - Documents/
   └── {Customer}/
       └── {Facility Address}/
           ├── As Built/
           └── Opp #{OpportunityNumber}- {ProjectName}/
               ├── DWG/
               ├── PDF/
               ├── Calculations/
               ├── Vendors/
               ├── Purchase Order/
               ├── Photos/
               ├── PPT/
               └── Proposals/
   ```

5. **File Management**: DWG and PDF files are moved to appropriate subfolders

6. **Email Notification**: Project manager and drafter receive email requesting Seizmic data

7. **Optional Seizmic Integration**: If enabled, portal form is submitted with provided data

## Configuration Files

### settings.ini
Main configuration file with all system settings:
```ini
[FileMonitoring]
watch_folder = C:\Users\*\World Class Integration\Projects - Documents
file_extensions = dwg,pdf
polling_interval = 5

[Odoo]
url = https://intralog.odoo.com/odoo
username = 
password = 
default_tags = Auto-Intake

[SharePoint]
site_id = 
drive_id = 
tenant_id = 
client_id = 
client_secret = 
base_folder = Projects - Documents

[Email]
smtp_server = smtp.gmail.com
smtp_port = 587
sender_email = agent@intralog.io
sender_password = 
use_tls = true

[Seizmic]
portal_url = https://portal.seizmicinc.com/
username = 
password = 
enabled = false

[Logging]
log_level = INFO
log_file = racking_automation.log
max_log_size = 10485760
backup_count = 5
```

### credentials.enc
Encrypted credential storage (created automatically when saving configuration)

## Logging

The system provides comprehensive logging:

- **Main Log**: `logs/racking_automation.log` - All system activities
- **Error Log**: `logs/errors.log` - Error-level messages only
- **Audit Log**: `logs/audit.log` - User actions and system changes

Log files are automatically rotated when they reach the configured size limit.

## Name-to-Email Mappings

The system includes built-in mappings for team members:

**Project Managers:**
- Aaron Cendejas → aaron@intralog.io
- Mark Westover → mark@intralog.io
- Indigo Allen → indigo@intralog.io

**Drafters:**
- Vanya Andonova → vanya@intralog.io
- Aaron Cendejas → aaron@intralog.io
- Michael Schulte → michael@intralog.io

These mappings can be updated in the `config.py` file as needed.

## Error Handling

The system includes robust error handling:

- **Retry Logic**: Failed operations are automatically retried with exponential backoff
- **Backup Creation**: Files are backed up before processing
- **Graceful Degradation**: Individual component failures don't stop the entire system
- **Detailed Logging**: All errors are logged with full context and stack traces
- **Recovery Mechanisms**: System can recover from temporary service outages

## Troubleshooting

### Common Issues

1. **File Monitoring Not Working**:
   - Verify watch folder exists and is accessible
   - Check file permissions
   - Ensure no other processes are locking files

2. **Odoo Login Failures**:
   - Verify credentials in configuration
   - Check if Chrome/ChromeDriver is properly installed
   - Test manual login to Odoo

3. **SharePoint Connection Issues**:
   - Verify Azure app permissions
   - Check Site ID and Drive ID are correct
   - Test connection using built-in test feature

4. **Email Delivery Problems**:
   - Verify SMTP server settings
   - Check sender credentials
   - Ensure TLS/SSL settings match server requirements

### Debug Mode

To enable detailed debugging:
1. Open configuration GUI
2. Go to General tab
3. Set Log Level to "DEBUG"
4. Save configuration and restart

### Log Analysis

Check the following logs for troubleshooting:
- `logs/racking_automation.log` - General system activity
- `logs/errors.log` - Error details
- `logs/audit.log` - User actions and configuration changes

## Development

### Architecture

The system follows a modular service-oriented architecture:

- **main.py**: Application entry point and orchestration
- **file_monitor.py**: File system monitoring and event handling
- **pdf_parser.py**: PDF text extraction and metadata parsing
- **odoo_automation.py**: Selenium-based Odoo integration
- **sharepoint_client.py**: Microsoft Graph API client
- **email_handler.py**: SMTP email automation
- **gui_config.py**: Tkinter-based configuration interface
- **config.py**: Configuration management
- **credential_manager.py**: Encrypted credential storage
- **logger_config.py**: Logging system configuration
- **utils.py**: Utility functions and helpers

### Adding New Features

1. Create new module following existing patterns
2. Add configuration options to `config.py`
3. Update GUI interface in `gui_config.py`
4. Add tests and documentation
5. Update this README

### Testing

The system includes connection testing for all integrated services:
- Use the "Test Connection" buttons in the configuration GUI
- Check logs for detailed test results
- Verify credentials and permissions before deployment

## Security Considerations

- Store all credentials in the encrypted credential manager
- Use environment variables for sensitive configuration in production
- Regularly rotate passwords and API keys
- Monitor audit logs for unauthorized access
- Keep dependencies updated for security patches

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review log files for error details
3. Verify configuration settings
4. Test individual components using built-in test features

## License

This project is proprietary software developed for Intralog. All rights reserved.

## Changelog

### Version 1.0.0 (August 2025)
- Initial release
- Complete workflow automation from file detection to SharePoint organization
- GUI configuration interface
- Encrypted credential storage
- Comprehensive logging and error handling
- Support for all major integrations (Odoo, SharePoint, Email, Seizmic)