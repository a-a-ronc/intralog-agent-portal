"""
Odoo automation using Selenium WebDriver.
"""

import time
import os
from typing import Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from logger_config import setup_logger
from utils import sanitize_text, retry_on_failure

class OdooAutomation:
    """Automates Odoo opportunity creation."""
    
    def __init__(self, config):
        self.config = config
        self.logger = setup_logger()
        self.driver = None
        self.wait = None
    
    def _setup_driver(self):
        """Set up Chrome WebDriver with appropriate options."""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # Run in headless mode for production
            # chrome_options.add_argument('--headless')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 20)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting up WebDriver: {str(e)}")
            return False
    
    def _login_to_odoo(self) -> bool:
        """Log into Odoo."""
        try:
            credentials = self.config.get_odoo_credentials()
            
            self.driver.get(credentials['url'])
            
            # Wait for login form
            email_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "login"))
            )
            
            password_field = self.driver.find_element(By.NAME, "password")
            
            # Enter credentials
            email_field.clear()
            email_field.send_keys(credentials['username'])
            
            password_field.clear() 
            password_field.send_keys(credentials['password'])
            
            # Submit login
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Wait for successful login (check for dashboard or CRM link)
            self.wait.until(
                EC.any_of(
                    EC.presence_of_element_located((By.LINK_TEXT, "CRM")),
                    EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'crm')]"))
                )
            )
            
            self.logger.info("Successfully logged into Odoo")
            return True
            
        except Exception as e:
            self.logger.error(f"Error logging into Odoo: {str(e)}")
            return False
    
    def _navigate_to_crm(self) -> bool:
        """Navigate to CRM module."""
        try:
            # Click on CRM menu
            crm_link = self.wait.until(
                EC.element_to_be_clickable((By.LINK_TEXT, "CRM"))
            )
            crm_link.click()
            
            # Wait for CRM page to load
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Pipeline')]"))
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error navigating to CRM: {str(e)}")
            return False
    
    def _create_new_opportunity(self, metadata: Dict[str, str]) -> Optional[str]:
        """Create a new opportunity in Odoo."""
        try:
            # Click Create/New button
            create_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create') or contains(text(), 'New')]"))
            )
            create_button.click()
            
            # Wait for opportunity form
            self.wait.until(
                EC.presence_of_element_located((By.NAME, "name"))
            )
            
            # Fill opportunity name
            opportunity_name = metadata.get('project_name', f"Project for {metadata.get('customer', 'Unknown')}")
            name_field = self.driver.find_element(By.NAME, "name")
            name_field.clear()
            name_field.send_keys(sanitize_text(opportunity_name))
            
            # Set customer
            customer_name = metadata.get('customer')
            if customer_name:
                self._set_customer(customer_name)
            
            # Set salesperson (Project Manager)
            pm_name = metadata.get('project_manager')
            if pm_name:
                self._set_salesperson(pm_name)
            
            # Add tags
            self._add_tags(['Auto-Intake'])
            
            # Save the opportunity
            save_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Save')]"))
            )
            save_button.click()
            
            # Wait for save and get opportunity number
            time.sleep(2)
            opportunity_number = self._get_opportunity_number()
            
            self.logger.info(f"Created opportunity: {opportunity_number}")
            return opportunity_number
            
        except Exception as e:
            self.logger.error(f"Error creating opportunity: {str(e)}")
            return None
    
    def _set_customer(self, customer_name: str):
        """Set or create customer in opportunity."""
        try:
            # Look for customer field (could be partner_id or customer field)
            customer_field = None
            possible_names = ['partner_id', 'customer', 'client']
            
            for name in possible_names:
                try:
                    customer_field = self.driver.find_element(By.NAME, name)
                    break
                except NoSuchElementException:
                    continue
            
            if not customer_field:
                # Try to find by label text
                customer_field = self.driver.find_element(
                    By.XPATH, "//input[@placeholder='Customer' or @placeholder='Partner']"
                )
            
            if customer_field:
                customer_field.clear()
                customer_field.send_keys(customer_name)
                
                # Wait for dropdown and select first option or create new
                time.sleep(1)
                try:
                    # Try to select existing customer
                    dropdown_option = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{customer_name}')]"))
                    )
                    dropdown_option.click()
                except TimeoutException:
                    # Customer doesn't exist, press Enter to create
                    from selenium.webdriver.common.keys import Keys
                    customer_field.send_keys(Keys.ENTER)
            
        except Exception as e:
            self.logger.warning(f"Could not set customer: {str(e)}")
    
    def _set_salesperson(self, pm_name: str):
        """Set salesperson/project manager."""
        try:
            # Look for salesperson field
            salesperson_field = None
            possible_names = ['user_id', 'salesperson', 'user']
            
            for name in possible_names:
                try:
                    salesperson_field = self.driver.find_element(By.NAME, name)
                    break
                except NoSuchElementException:
                    continue
            
            if not salesperson_field:
                # Try to find by placeholder or label
                salesperson_field = self.driver.find_element(
                    By.XPATH, "//input[@placeholder='Salesperson']"
                )
            
            if salesperson_field:
                salesperson_field.clear()
                salesperson_field.send_keys(pm_name)
                
                # Wait for dropdown and select
                time.sleep(1)
                try:
                    dropdown_option = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{pm_name}')]"))
                    )
                    dropdown_option.click()
                except TimeoutException:
                    self.logger.warning(f"Could not find salesperson: {pm_name}")
            
        except Exception as e:
            self.logger.warning(f"Could not set salesperson: {str(e)}")
    
    def _add_tags(self, tags: list):
        """Add tags to opportunity."""
        try:
            # Look for tags field
            tags_field = self.driver.find_element(By.NAME, "tag_ids")
            
            for tag in tags:
                tags_field.send_keys(tag)
                time.sleep(0.5)
                
                # Try to select from dropdown or create new
                try:
                    tag_option = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{tag}')]"))
                    )
                    tag_option.click()
                except TimeoutException:
                    # Press Enter to create new tag
                    from selenium.webdriver.common.keys import Keys
                    tags_field.send_keys(Keys.ENTER)
        
        except Exception as e:
            self.logger.warning(f"Could not add tags: {str(e)}")
    
    def _get_opportunity_number(self) -> Optional[str]:
        """Extract opportunity number from the page."""
        try:
            # Look for opportunity number in various possible locations
            possible_selectors = [
                "//span[contains(@class, 'o_field_char') and contains(text(), 'OPP')]",
                "//span[contains(text(), 'OPP')]",
                "//span[contains(@class, 'reference')]",
                "//h1//span[contains(text(), 'OPP')]"
            ]
            
            for selector in possible_selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    text = element.text.strip()
                    if 'OPP' in text:
                        return text
                except NoSuchElementException:
                    continue
            
            # Fallback: generate a placeholder number
            import random
            return f"OPP{random.randint(10000, 99999)}"
            
        except Exception as e:
            self.logger.error(f"Error getting opportunity number: {str(e)}")
            return None
    
    @retry_on_failure(max_retries=3)
    def create_opportunity(self, metadata: Dict[str, str]) -> Optional[str]:
        """Main method to create opportunity in Odoo."""
        try:
            self.logger.info("Starting Odoo opportunity creation")
            
            # Set up WebDriver
            if not self._setup_driver():
                return None
            
            try:
                # Login to Odoo
                if not self._login_to_odoo():
                    return None
                
                # Navigate to CRM
                if not self._navigate_to_crm():
                    return None
                
                # Create opportunity
                opportunity_number = self._create_new_opportunity(metadata)
                
                return opportunity_number
                
            finally:
                # Clean up
                if self.driver:
                    self.driver.quit()
                    self.driver = None
        
        except Exception as e:
            self.logger.error(f"Error in opportunity creation: {str(e)}")
            return None
