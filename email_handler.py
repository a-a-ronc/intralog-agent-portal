"""
Email automation for Seizmic data collection and notifications.
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
import re

from logger_config import setup_logger

class EmailHandler:
    """Handles email automation for the system."""
    
    def __init__(self, config):
        self.config = config
        self.logger = setup_logger()
    
    def _create_smtp_connection(self):
        """Create SMTP connection."""
        try:
            email_config = self.config.get_email_credentials()
            
            # Create SMTP connection
            if email_config['use_tls']:
                context = ssl.create_default_context()
                server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
                server.starttls(context=context)
            else:
                server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            
            # Login
            server.login(email_config['sender_email'], email_config['sender_password'])
            
            return server
            
        except Exception as e:
            self.logger.error(f"Error creating SMTP connection: {str(e)}")
            return None
    
    def send_seizmic_data_request(self, metadata: Dict[str, str], opportunity_number: str) -> bool:
        """Send email requesting Seizmic portal data."""
        try:
            self.logger.info("Sending Seizmic data request email")
            
            # Get recipient emails
            pm_name = metadata.get('project_manager', '')
            drafter_name = metadata.get('drafter', '')
            
            pm_email = self.config.get_pm_email(pm_name)
            drafter_email = self.config.get_drafter_email(drafter_name)
            
            if not pm_email:
                self.logger.error(f"No email found for PM: {pm_name}")
                return False
            
            # Prepare email
            subject = f"Seizmic Data Required - Opp {opportunity_number} - {metadata.get('customer', 'Unknown')}"
            
            body = self._create_seizmic_request_body(metadata, opportunity_number)
            
            # Set recipients
            to_emails = [pm_email]
            cc_emails = [drafter_email] if drafter_email and drafter_email != pm_email else []
            
            # Send email
            success = self._send_email(subject, body, to_emails, cc_emails)
            
            if success:
                self.logger.info(f"Seizmic data request sent to {pm_email}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending Seizmic data request: {str(e)}")
            return False
    
    def _create_seizmic_request_body(self, metadata: Dict[str, str], opportunity_number: str) -> str:
        """Create email body for Seizmic data request."""
        customer = metadata.get('customer', 'Unknown')
        address = metadata.get('address', 'Unknown')
        project_name = metadata.get('project_name', 'Project')
        
        body = f"""
Dear {metadata.get('project_manager', 'Project Manager')},

A new opportunity has been automatically created in Odoo:

Opportunity Number: {opportunity_number}
Customer: {customer}
Facility Address: {address}
Project: {project_name}
Drafter: {metadata.get('drafter', 'Unknown')}

To complete the Seizmic portal submission, please reply to this email with the following information:

1. Prelim Type: ________________
2. Manufacturer: _______________
3. Rack Type: _________________
4. Anchor Type: _______________

Once this information is provided, the Seizmic portal form will be automatically submitted.

The project files have been organized in SharePoint at:
/Projects - Documents/{customer}/{address}/Opp {opportunity_number}- {project_name}/

Best regards,
Racking PM Automation System
"""
        return body
    
    def send_notification(self, subject: str, message: str, recipients: List[str]) -> bool:
        """Send general notification email."""
        try:
            return self._send_email(subject, message, recipients)
            
        except Exception as e:
            self.logger.error(f"Error sending notification: {str(e)}")
            return False
    
    def send_error_notification(self, error_message: str, context: Dict[str, str]) -> bool:
        """Send error notification to administrators."""
        try:
            subject = "Racking PM Automation - Error Notification"
            
            body = f"""
An error occurred in the Racking PM Automation system:

Error: {error_message}

Context:
"""
            for key, value in context.items():
                body += f"{key}: {value}\n"
            
            body += f"""
Please check the system logs for more details.

Timestamp: {context.get('timestamp', 'Unknown')}
"""
            
            # Send to system administrators
            admin_emails = ['admin@intralog.io']  # Configure as needed
            
            return self._send_email(subject, body, admin_emails)
            
        except Exception as e:
            self.logger.error(f"Error sending error notification: {str(e)}")
            return False
    
    def _send_email(self, subject: str, body: str, to_emails: List[str], cc_emails: List[str] = None) -> bool:
        """Send email using SMTP."""
        try:
            if not to_emails:
                self.logger.error("No recipients specified")
                return False
            
            email_config = self.config.get_email_credentials()
            
            # Create message
            message = MIMEMultipart()
            message["From"] = email_config['sender_email']
            message["To"] = ", ".join(to_emails)
            
            if cc_emails:
                message["Cc"] = ", ".join(cc_emails)
            
            message["Subject"] = subject
            
            # Add body
            message.attach(MIMEText(body, "plain"))
            
            # Create SMTP connection and send
            server = self._create_smtp_connection()
            if not server:
                return False
            
            try:
                # Prepare recipient list
                all_recipients = to_emails[:]
                if cc_emails:
                    all_recipients.extend(cc_emails)
                
                # Send email
                text = message.as_string()
                server.sendmail(email_config['sender_email'], all_recipients, text)
                
                self.logger.info(f"Email sent successfully to {', '.join(all_recipients)}")
                return True
                
            finally:
                server.quit()
                
        except Exception as e:
            self.logger.error(f"Error sending email: {str(e)}")
            return False
    
    def parse_seizmic_reply(self, email_content: str) -> Optional[Dict[str, str]]:
        """Parse Seizmic data from email reply."""
        try:
            # Extract Seizmic data using regex patterns
            patterns = {
                'prelim_type': r'prelim\s+type[:\s]+([^\n\r]+)',
                'manufacturer': r'manufacturer[:\s]+([^\n\r]+)',
                'rack_type': r'rack\s+type[:\s]+([^\n\r]+)',
                'anchor_type': r'anchor\s+type[:\s]+([^\n\r]+)'
            }
            
            data = {}
            email_lower = email_content.lower()
            
            for field, pattern in patterns.items():
                match = re.search(pattern, email_lower, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    # Clean up common artifacts
                    value = re.sub(r'_{3,}', '', value)  # Remove underscores
                    data[field] = value
            
            return data if data else None
            
        except Exception as e:
            self.logger.error(f"Error parsing Seizmic reply: {str(e)}")
            return None
    
    def validate_email_address(self, email: str) -> bool:
        """Validate email address format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
