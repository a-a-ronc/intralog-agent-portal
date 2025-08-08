"""
SharePoint client for folder creation and file management via Microsoft Graph API.
"""

import os
import requests
import json
from typing import Dict, Optional, List
from pathlib import Path
import msal

from logger_config import setup_logger
from utils import sanitize_filename, retry_on_failure

class SharePointClient:
    """Microsoft Graph API client for SharePoint operations."""
    
    def __init__(self, config):
        self.config = config
        self.logger = setup_logger()
        self.access_token = None
        self.base_url = "https://graph.microsoft.com/v1.0"
        
        # Subfolder structure to create
        self.subfolders = [
            "DWG",
            "PDF", 
            "Calculations",
            "Vendors",
            "Purchase Order",
            "Photos",
            "PPT",
            "Proposals"
        ]
    
    def _get_access_token(self) -> bool:
        """Get access token using MSAL."""
        try:
            credentials = self.config.get_sharepoint_credentials()
            
            # Create MSAL app
            app = msal.ConfidentialClientApplication(
                client_id=credentials['client_id'],
                client_credential=credentials['client_secret'],
                authority=f"https://login.microsoftonline.com/{credentials['tenant_id']}"
            )
            
            # Get token using client credentials flow
            scopes = ["https://graph.microsoft.com/.default"]
            result = app.acquire_token_for_client(scopes=scopes)
            
            if "access_token" in result:
                self.access_token = result["access_token"]
                return True
            else:
                self.logger.error(f"Failed to get access token: {result.get('error_description')}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error getting access token: {str(e)}")
            return False
    
    def _make_graph_request(self, method: str, endpoint: str, data: dict = None) -> Optional[dict]:
        """Make a request to Microsoft Graph API."""
        try:
            if not self.access_token:
                if not self._get_access_token():
                    return None
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.base_url}/{endpoint}"
            
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, json=data)
            elif method.upper() == 'PATCH':
                response = requests.patch(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            if response.status_code == 401:
                # Token expired, try to refresh
                self.access_token = None
                if self._get_access_token():
                    headers['Authorization'] = f'Bearer {self.access_token}'
                    response = requests.request(method, url, headers=headers, json=data)
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                self.logger.error(f"Graph API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error making Graph request: {str(e)}")
            return None
    
    def _create_folder(self, parent_path: str, folder_name: str) -> Optional[str]:
        """Create a folder in SharePoint."""
        try:
            credentials = self.config.get_sharepoint_credentials()
            site_id = credentials['site_id']
            drive_id = credentials['drive_id']
            
            # Sanitize folder name
            safe_folder_name = sanitize_filename(folder_name)
            
            # Build endpoint
            if parent_path == '/':
                endpoint = f"sites/{site_id}/drives/{drive_id}/root/children"
            else:
                encoded_path = requests.utils.quote(parent_path.strip('/'), safe='/')
                endpoint = f"sites/{site_id}/drives/{drive_id}/root:/{encoded_path}:/children"
            
            # Create folder
            folder_data = {
                "name": safe_folder_name,
                "folder": {},
                "@microsoft.graph.conflictBehavior": "rename"
            }
            
            result = self._make_graph_request('POST', endpoint, folder_data)
            
            if result:
                folder_path = f"{parent_path.rstrip('/')}/{safe_folder_name}"
                self.logger.info(f"Created folder: {folder_path}")
                return folder_path
            else:
                self.logger.error(f"Failed to create folder: {safe_folder_name}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error creating folder: {str(e)}")
            return None
    
    def _build_project_path(self, metadata: Dict[str, str], opportunity_number: str) -> str:
        """Build the project folder path."""
        customer = sanitize_filename(metadata.get('customer', 'Unknown Customer'))
        address = sanitize_filename(metadata.get('address', 'Unknown Address'))
        project_name = sanitize_filename(metadata.get('project_name', 'Project'))
        
        # Build path: /Projects - Documents/{Customer}/{Address}/Opp #{OppNo}- {ProjectName}/
        base_folder = self.config.get('SharePoint', 'base_folder', 'Projects - Documents')
        project_path = f"/{base_folder}/{customer}/{address}/Opp {opportunity_number}- {project_name}"
        
        return project_path
    
    @retry_on_failure(max_retries=3)
    def create_folder_structure(self, metadata: Dict[str, str], opportunity_number: str) -> Optional[str]:
        """Create the complete folder structure for a project."""
        try:
            self.logger.info("Creating SharePoint folder structure")
            
            # Build project path
            project_path = self._build_project_path(metadata, opportunity_number)
            
            # Create folder hierarchy
            path_parts = [part for part in project_path.split('/') if part]
            current_path = '/'
            
            for part in path_parts:
                folder_path = self._create_folder(current_path, part)
                if folder_path:
                    current_path = folder_path
                else:
                    self.logger.error(f"Failed to create folder part: {part}")
                    return None
            
            # Create subfolders
            for subfolder in self.subfolders:
                subfolder_path = self._create_folder(current_path, subfolder)
                if not subfolder_path:
                    self.logger.warning(f"Failed to create subfolder: {subfolder}")
            
            # Create "As Built" folder at facility address level
            address_path = '/'.join(current_path.split('/')[:-1])  # Remove opportunity folder
            as_built_path = self._create_folder(address_path, "As Built")
            
            self.logger.info(f"Created folder structure at: {current_path}")
            return current_path
            
        except Exception as e:
            self.logger.error(f"Error creating folder structure: {str(e)}")
            return None
    
    def _upload_file(self, local_file_path: str, sharepoint_folder_path: str, filename: str) -> bool:
        """Upload a file to SharePoint."""
        try:
            credentials = self.config.get_sharepoint_credentials()
            site_id = credentials['site_id']
            drive_id = credentials['drive_id']
            
            # Read file content
            with open(local_file_path, 'rb') as f:
                file_content = f.read()
            
            # Build upload endpoint
            encoded_path = requests.utils.quote(f"{sharepoint_folder_path.strip('/')}/{filename}", safe='/')
            endpoint = f"sites/{site_id}/drives/{drive_id}/root:/{encoded_path}:/content"
            
            # Upload file
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/octet-stream'
            }
            
            response = requests.put(f"{self.base_url}/{endpoint}", headers=headers, data=file_content)
            
            if response.status_code in [200, 201]:
                self.logger.info(f"Uploaded file: {filename} to {sharepoint_folder_path}")
                return True
            else:
                self.logger.error(f"Failed to upload file: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error uploading file: {str(e)}")
            return False
    
    def move_files_to_sharepoint(self, pdf_file: str, dwg_file: str, project_folder_path: str) -> bool:
        """Move DWG and PDF files to appropriate SharePoint subfolders."""
        try:
            self.logger.info("Moving files to SharePoint")
            
            if not self.access_token:
                if not self._get_access_token():
                    return False
            
            # Upload PDF to PDF subfolder
            pdf_filename = os.path.basename(pdf_file)
            pdf_success = self._upload_file(
                pdf_file, 
                f"{project_folder_path}/PDF", 
                pdf_filename
            )
            
            # Upload DWG to DWG subfolder
            dwg_filename = os.path.basename(dwg_file)
            dwg_success = self._upload_file(
                dwg_file,
                f"{project_folder_path}/DWG",
                dwg_filename
            )
            
            # Delete local files if upload successful
            if pdf_success and dwg_success:
                try:
                    os.remove(pdf_file)
                    os.remove(dwg_file)
                    self.logger.info("Local files removed after successful upload")
                except Exception as e:
                    self.logger.warning(f"Could not remove local files: {str(e)}")
                
                return True
            else:
                self.logger.error("File upload failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Error moving files to SharePoint: {str(e)}")
            return False
    
    def test_connection(self) -> bool:
        """Test SharePoint connection by creating and deleting a temp folder."""
        try:
            self.logger.info("Testing SharePoint connection")
            
            if not self._get_access_token():
                return False
            
            # Try to create a test folder
            test_folder = self._create_folder('/', 'TEST_CONNECTION_DELETE_ME')
            
            if test_folder:
                # Delete the test folder
                credentials = self.config.get_sharepoint_credentials()
                site_id = credentials['site_id']
                drive_id = credentials['drive_id']
                
                encoded_path = requests.utils.quote(test_folder.strip('/'), safe='/')
                endpoint = f"sites/{site_id}/drives/{drive_id}/root:/{encoded_path}"
                
                delete_result = self._make_graph_request('DELETE', endpoint)
                
                self.logger.info("SharePoint connection test successful")
                return True
            else:
                self.logger.error("SharePoint connection test failed")
                return False
                
        except Exception as e:
            self.logger.error(f"SharePoint connection test error: {str(e)}")
            return False
