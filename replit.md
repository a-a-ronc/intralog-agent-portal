# Racking PM Automation System

## Overview

This is a desktop automation system that monitors file changes, extracts metadata from PDFs, creates opportunities in Odoo, manages SharePoint folders, and handles email notifications. The system is designed to streamline project management workflows by automating the detection of DWG/PDF file pairs and triggering a series of automated actions including opportunity creation, document organization, and stakeholder notifications.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Architecture Pattern
The system follows a **modular service-oriented architecture** with clear separation of concerns. Each major functionality is encapsulated in its own module, allowing for independent testing, maintenance, and potential scaling.

### File Monitoring System
- **Problem**: Need to detect when new DWG/PDF file pairs are added to monitored directories
- **Solution**: Watchdog-based file system monitoring with configurable polling intervals
- **Components**: 
  - `FileMonitor` class using watchdog library for real-time file system events
  - `FileProcessor` class handling the business logic for file pair processing
- **Rationale**: Real-time monitoring ensures immediate response to new files without manual intervention

### Data Extraction Pipeline
- **Problem**: Extract structured metadata from PDF title blocks containing project information
- **Solution**: PDF parsing using pdfplumber with regex pattern matching
- **Components**: 
  - `PDFParser` class with configurable regex patterns for different title block formats
  - Pattern-based extraction supporting customer, address, project manager, drafter, and project name fields
- **Rationale**: Flexible pattern matching accommodates various PDF formats while maintaining accuracy

### Web Automation Framework
- **Problem**: Automate Odoo opportunity creation without direct API access
- **Solution**: Selenium WebDriver automation with Chrome browser
- **Components**:
  - `OdooAutomation` class handling login, form filling, and opportunity creation
  - Retry mechanisms and error handling for web element interactions
- **Rationale**: Web automation provides reliable integration when APIs are not available or accessible

### Configuration Management
- **Problem**: Manage multiple configuration sources and credential storage securely
- **Solution**: Layered configuration with encrypted credential storage
- **Components**:
  - `Config` class for application settings using ConfigParser
  - `CredentialManager` class for encrypted credential storage using Fernet encryption
  - `ConfigGUI` for user-friendly configuration management
- **Rationale**: Separation of configuration from code enables environment-specific deployments and secure credential handling

### Integration Layer
- **Problem**: Coordinate multiple external services (SharePoint, Odoo, Email) in a workflow
- **Solution**: Service-specific client classes with unified error handling and logging
- **Components**:
  - `SharePointClient` using Microsoft Graph API for folder management
  - `EmailHandler` for SMTP-based notifications
  - Centralized logging system with rotation and different output levels
- **Rationale**: Service isolation allows independent testing and maintenance of integrations

### User Interface Design
- **Problem**: Provide accessible configuration without technical complexity
- **Solution**: Tkinter-based GUI with tabbed interface
- **Components**:
  - Tab-based configuration for different service categories
  - Real-time validation and test connectivity features
  - Status monitoring and control buttons
- **Rationale**: Desktop GUI provides familiar interface for non-technical users while maintaining full functionality

### Error Handling Strategy
- **Problem**: Ensure system reliability despite external service failures
- **Solution**: Multi-layered error handling with retry mechanisms and fallback procedures
- **Components**:
  - Decorator-based retry logic for transient failures
  - Comprehensive logging for debugging and monitoring
  - Backup file creation before processing
- **Rationale**: Robust error handling prevents data loss and enables automatic recovery from temporary issues

## External Dependencies

### Authentication & APIs
- **Microsoft Graph API**: SharePoint folder creation and file management using OAuth 2.0 client credentials flow
- **MSAL (Microsoft Authentication Library)**: Token acquisition and management for Microsoft 365 integration

### Web Automation
- **Selenium WebDriver**: Chrome browser automation for Odoo interaction
- **Chrome Browser**: Required for web automation tasks

### Document Processing
- **pdfplumber**: PDF text extraction and metadata parsing
- **pathlib**: Cross-platform file system operations

### Security & Encryption
- **cryptography (Fernet)**: Symmetric encryption for credential storage
- **PBKDF2HMAC**: Key derivation for password-based encryption

### File System Monitoring
- **watchdog**: Cross-platform file system event monitoring
- **threading**: Asynchronous file monitoring and processing

### Communication
- **smtplib**: Email sending for notifications and data requests
- **ssl**: Secure email connections

### User Interface
- **tkinter**: Desktop GUI framework for configuration management
- **ttk**: Enhanced UI widgets for modern appearance

### Configuration & Logging
- **configparser**: INI-style configuration file management
- **logging**: Structured application logging with rotation
- **json**: Configuration and data serialization

### HTTP & API Communication
- **requests**: HTTP client for REST API interactions
- **msal**: Microsoft-specific authentication flows