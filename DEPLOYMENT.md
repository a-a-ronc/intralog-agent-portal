# Deployment Guide for Racking PM Automation System

## Quick Deployment Steps

Since git operations are restricted in this environment, you'll need to manually deploy the code to your GitHub repository. Here's how:

### 1. Download Project Files

Copy all the following files from this environment to your local machine:

**Core Application Files:**
- `main.py` - Application entry point
- `config.py` - Configuration management
- `file_monitor.py` - File system monitoring
- `pdf_parser.py` - PDF metadata extraction
- `odoo_automation.py` - Odoo integration
- `sharepoint_client.py` - SharePoint API client
- `email_handler.py` - Email automation
- `gui_config.py` - Configuration GUI
- `credential_manager.py` - Secure credential storage
- `logger_config.py` - Logging configuration
- `utils.py` - Utility functions

**Configuration Files:**
- `settings.ini` - Application settings (remove credentials before committing)
- `replit.md` - Project documentation

**Documentation:**
- `README.md` - Complete project documentation
- `DEPLOYMENT.md` - This deployment guide
- `dependencies.txt` - Python dependencies list

### 2. Git Repository Setup

```bash
# Navigate to your local project directory
cd path/to/your/project

# Initialize git repository (if not already done)
git init

# Add remote repository
git remote add origin https://github.com/a-a-ronc/intralog-agent-portal.git

# Add all files
git add .

# Commit the initial version
git commit -m "Initial commit: Racking PM Automation System v1.0

- Complete desktop automation for DWG/PDF file monitoring
- PDF title block parsing with metadata extraction
- Selenium-based Odoo opportunity creation
- Microsoft Graph SharePoint integration
- SMTP email automation with templates
- Secure encrypted credential storage
- Comprehensive GUI configuration interface
- Robust error handling and logging system"

# Push to GitHub
git push -u origin main
```

### 3. Environment Setup

On the target deployment machine:

```bash
# Clone the repository
git clone https://github.com/a-a-ronc/intralog-agent-portal.git
cd intralog-agent-portal

# Install Python dependencies
pip install -r dependencies.txt

# Or install individually:
pip install watchdog pdfplumber selenium msal cryptography requests
```

### 4. Production Configuration

1. **Run Initial Configuration:**
   ```bash
   python main.py --config
   ```

2. **Configure Required Services:**
   - **File Monitoring**: Set the correct watch folder path
   - **Odoo**: Enter production Odoo credentials
   - **SharePoint**: Configure Azure app credentials with proper permissions
   - **Email**: Set up SMTP server details for notifications

3. **Test All Connections:**
   - Use the "Test Connection" buttons in each tab
   - Verify all services are accessible
   - Check log files for any issues

### 5. Azure App Registration (SharePoint)

For SharePoint integration, you need an Azure app with these permissions:

```
API Permissions:
- Microsoft Graph: Sites.Read.All (Application)
- Microsoft Graph: Files.ReadWrite.All (Application)
- Microsoft Graph: User.Read (Delegated)
- Microsoft Graph: offline_access (Delegated)
```

**Setup Steps:**
1. Go to Azure Portal → App Registrations
2. Create new app registration
3. Add the required API permissions
4. Grant admin consent
5. Create client secret
6. Note down: Tenant ID, Client ID, Client Secret

### 6. SharePoint Site Configuration

Get your SharePoint Site ID and Drive ID:

**Method 1: Using Graph Explorer**
1. Go to https://developer.microsoft.com/graph/graph-explorer
2. Query: `GET https://graph.microsoft.com/v1.0/sites/{hostname}:{sitePath}`
3. Query: `GET https://graph.microsoft.com/v1.0/sites/{siteId}/drives`

**Method 2: Using PowerShell**
```powershell
# Install Microsoft.Graph module
Install-Module Microsoft.Graph

# Connect to Graph
Connect-MgGraph -Scopes "Sites.Read.All"

# Get site
Get-MgSite -Search "Projects"

# Get drives for site
Get-MgSiteDrive -SiteId "{site-id}"
```

### 7. Production Deployment Options

**Option A: Windows Service (Recommended)**
1. Install as Windows service for automatic startup
2. Use tools like `nssm` or `sc create`
3. Configure service to restart on failure

**Option B: Scheduled Task**
1. Create Windows scheduled task
2. Set to run at startup with system privileges
3. Configure restart policies

**Option C: Console Application**
```bash
# Run in console mode for production
python main.py --console
```

### 8. Monitoring and Maintenance

**Log Monitoring:**
- Check `logs/racking_automation.log` for general activity
- Monitor `logs/errors.log` for system issues
- Review `logs/audit.log` for configuration changes

**Health Checks:**
- Test file monitoring by placing test files
- Verify SharePoint connectivity
- Check email delivery
- Monitor Odoo integration

**Regular Maintenance:**
- Rotate log files (automatic)
- Update credentials as needed
- Backup configuration and logs
- Update dependencies periodically

### 9. Security Considerations

**Credential Protection:**
- All credentials are encrypted in `credentials.enc`
- Use strong master password
- Regular credential rotation
- Backup credential file securely

**Access Control:**
- Limit file system permissions to service account
- Use dedicated service account for automation
- Monitor audit logs for unauthorized access

**Network Security:**
- Use TLS for all external communications
- Firewall rules for necessary ports only
- VPN access for remote administration

### 10. Troubleshooting

**Common Issues:**
1. **Chrome/ChromeDriver**: Ensure latest versions installed
2. **File Permissions**: Service account needs read/write access
3. **Network Connectivity**: Check firewalls and proxy settings
4. **Credential Expiry**: Monitor and rotate credentials

**Debug Steps:**
1. Enable DEBUG logging level
2. Test individual components using GUI
3. Check Windows Event Viewer for service issues
4. Verify file paths and permissions

### 11. Backup Strategy

**What to Backup:**
- `settings.ini` (configuration)
- `credentials.enc` (encrypted credentials)
- `logs/` directory (system logs)
- Custom PDF parsing patterns (if modified)

**Backup Schedule:**
- Daily: Configuration and credentials
- Weekly: Complete logs archive
- Monthly: Full system backup

### 12. Version Control Best Practices

**Branch Strategy:**
- `main`: Production-ready code
- `develop`: Integration branch
- `feature/*`: New features
- `hotfix/*`: Critical fixes

**Commit Guidelines:**
- Clear, descriptive commit messages
- Reference issue numbers when applicable
- Tag releases with semantic versioning

**Release Process:**
1. Test in development environment
2. Update documentation
3. Create release tag
4. Deploy to production
5. Monitor for issues

### Support

For deployment issues:
1. Check this deployment guide
2. Review log files in `logs/` directory
3. Test components individually using the GUI
4. Verify all prerequisites are installed
5. Check network connectivity and permissions