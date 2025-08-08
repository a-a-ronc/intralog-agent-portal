#!/usr/bin/env python3
"""
Deployment helper script for Racking PM Automation System.
This script helps prepare the project for manual deployment to GitHub.
"""

import os
import shutil
import zipfile
import datetime
from pathlib import Path

def create_deployment_package():
    """Create a deployment package with all necessary files."""
    
    # Define files to include in deployment
    core_files = [
        'main.py',
        'config.py', 
        'file_monitor.py',
        'pdf_parser.py',
        'odoo_automation.py',
        'sharepoint_client.py',
        'email_handler.py',
        'gui_config.py',
        'credential_manager.py',
        'logger_config.py',
        'utils.py'
    ]
    
    config_files = [
        'settings.ini',
        'replit.md'
    ]
    
    doc_files = [
        'README.md',
        'DEPLOYMENT.md',
        'dependencies.txt',
        '.gitignore'
    ]
    
    # Create deployment directory
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    deploy_dir = Path(f"deployment_package_{timestamp}")
    deploy_dir.mkdir(exist_ok=True)
    
    print(f"Creating deployment package in: {deploy_dir}")
    
    # Copy files
    all_files = core_files + config_files + doc_files
    copied_files = []
    
    for file_name in all_files:
        if os.path.exists(file_name):
            shutil.copy2(file_name, deploy_dir / file_name)
            copied_files.append(file_name)
            print(f"✓ Copied: {file_name}")
        else:
            print(f"✗ Missing: {file_name}")
    
    # Clean settings.ini of sensitive data
    settings_file = deploy_dir / "settings.ini"
    if settings_file.exists():
        clean_settings_file(settings_file)
        print("✓ Cleaned sensitive data from settings.ini")
    
    # Create zip archive
    zip_name = f"racking_pm_automation_{timestamp}.zip"
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in deploy_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(deploy_dir)
                zipf.write(file_path, arcname)
    
    print(f"\n✓ Created deployment package: {zip_name}")
    print(f"✓ Total files included: {len(copied_files)}")
    
    # Create deployment instructions
    create_deployment_instructions(deploy_dir, copied_files)
    
    return deploy_dir, zip_name

def clean_settings_file(settings_path):
    """Remove sensitive information from settings.ini for GitHub."""
    
    sensitive_keys = [
        'username', 'password', 'sender_password', 
        'client_secret', 'site_id', 'drive_id', 
        'tenant_id', 'client_id'
    ]
    
    try:
        with open(settings_path, 'r') as f:
            lines = f.readlines()
        
        with open(settings_path, 'w') as f:
            for line in lines:
                # Check if line contains sensitive data
                if '=' in line:
                    key = line.split('=')[0].strip()
                    if key in sensitive_keys:
                        f.write(f"{key} = \n")
                    else:
                        f.write(line)
                else:
                    f.write(line)
                    
    except Exception as e:
        print(f"Warning: Could not clean settings file: {e}")

def create_deployment_instructions(deploy_dir, copied_files):
    """Create deployment instructions file."""
    
    instructions = f"""# Deployment Instructions

## Files Included in This Package

### Core Application Files ({len([f for f in copied_files if f.endswith('.py') and f != 'deploy.py'])} files):
{chr(10).join([f"- {f}" for f in copied_files if f.endswith('.py') and f != 'deploy.py'])}

### Configuration Files:
{chr(10).join([f"- {f}" for f in copied_files if f.endswith('.ini') or f.endswith('.md')])}

### Documentation:
{chr(10).join([f"- {f}" for f in copied_files if f in ['README.md', 'DEPLOYMENT.md', 'dependencies.txt', '.gitignore']])}

## Quick Deployment Steps

1. **Extract Files**: Extract this package to your project directory

2. **Initialize Git Repository**:
   ```bash
   git init
   git remote add origin https://github.com/a-a-ronc/intralog-agent-portal.git
   ```

3. **Commit and Push**:
   ```bash
   git add .
   git commit -m "Initial commit: Racking PM Automation System v1.0"
   git push -u origin main
   ```

4. **Production Setup**:
   - Clone repository on target machine
   - Install dependencies: `pip install -r dependencies.txt`
   - Configure settings: `python main.py --config`
   - Test all connections before going live

## Important Notes

- Sensitive data has been removed from settings.ini
- You'll need to reconfigure credentials in production
- See DEPLOYMENT.md for complete setup instructions
- See README.md for comprehensive documentation

## Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    
    with open(deploy_dir / "DEPLOYMENT_INSTRUCTIONS.txt", 'w') as f:
        f.write(instructions)

def display_git_commands():
    """Display git commands for manual deployment."""
    
    print("\n" + "="*60)
    print("GIT DEPLOYMENT COMMANDS")
    print("="*60)
    print("""
Since git operations are restricted in this environment, 
use these commands on your local machine:

1. Extract the deployment package to your local project directory

2. Initialize and configure git:
   git init
   git remote add origin https://github.com/a-a-ronc/intralog-agent-portal.git

3. Add and commit files:
   git add .
   git commit -m "Initial commit: Racking PM Automation System v1.0

   - Complete desktop automation for DWG/PDF monitoring
   - PDF title block parsing with metadata extraction  
   - Selenium-based Odoo opportunity creation
   - Microsoft Graph SharePoint integration
   - SMTP email automation with templates
   - Secure encrypted credential storage
   - GUI configuration interface
   - Robust error handling and logging"

4. Push to GitHub:
   git push -u origin main

5. For production deployment:
   git clone https://github.com/a-a-ronc/intralog-agent-portal.git
   cd intralog-agent-portal
   pip install -r dependencies.txt
   python main.py --config
""")
    print("="*60)

if __name__ == "__main__":
    print("Racking PM Automation - Deployment Package Creator")
    print("="*55)
    
    try:
        deploy_dir, zip_file = create_deployment_package()
        display_git_commands()
        
        print(f"\n✅ Deployment package ready!")
        print(f"📦 Package location: {zip_file}")
        print(f"📁 Extracted files: {deploy_dir}")
        print(f"\nNext steps:")
        print(f"1. Download the {zip_file} file")
        print(f"2. Extract on your local machine")
        print(f"3. Follow the git commands above")
        print(f"4. See DEPLOYMENT.md for production setup")
        
    except Exception as e:
        print(f"❌ Error creating deployment package: {e}")
        import traceback
        traceback.print_exc()