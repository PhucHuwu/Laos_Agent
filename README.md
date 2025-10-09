<div align="center">

# 🇱🇦 Laos eKYC Identity Verification System

### AI-Powered Electronic Know Your Customer (eKYC) Solution

[![Python Version](https://img.shields.io/badge/python-3.11.5-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

*A comprehensive eKYC system for Laotian citizen identity verification combining AI-powered chatbot technology, OCR document scanning, and real-time facial recognition.*

[Features](#-key-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [API Reference](#-api-reference) • [Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Technology Stack](#-technology-stack)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [API Reference](#-api-reference)
- [Module Documentation](#-module-documentation)
- [Development Guide](#-development-guide)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Security Considerations](#-security-considerations)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

The **Laos eKYC Identity Verification System** is a modern, AI-powered solution designed to streamline the identity verification process for Laotian citizens. The system leverages cutting-edge technologies including:

- **AI Chatbot** (Google Gemini 2.5 Flash Lite) for conversational user guidance in Lao language
- **OCR Technology** for automated document scanning and data extraction
- **Real-time Facial Recognition** using WebSocket for live verification
- **Automated Data Management** with cleanup and storage optimization

### Use Cases

- 🏦 **Banking & Financial Services**: Customer onboarding and KYC compliance
- 🏢 **Government Services**: Citizen identification and verification
- 📱 **Telecommunications**: SIM card registration and account verification
- 🏥 **Healthcare**: Patient registration and identity confirmation
- 🎓 **Education**: Student enrollment and identity verification

---

## 🚀 Key Features

### 💬 AI-Powered Conversational Interface
- **Lao Language Support**: Native Lao language interface for seamless user experience
- **Streaming Responses**: Real-time thinking and reasoning display
- **Context-Aware Conversations**: Maintains conversation history and context
- **Tool Call Management**: Intelligent orchestration of verification steps

### 📄 Document Processing
- **OCR Scanning**: Automatic extraction of data from Laotian ID cards
- **Image Upload**: Support for JPEG, PNG, JPG formats (up to 16MB)
- **Data Validation**: Automatic validation of extracted information
- **Formatted Display**: Clean, readable presentation of scan results

### 👤 Facial Verification
- **Batch Verification**: Single-shot face comparison
- **Real-time Verification**: Live camera feed processing via WebSocket
- **Multi-mode Support**: Both static image and live video verification
- **Confidence Scoring**: Detailed similarity scores and verification status

### 🧹 Data Management
- **Auto Cleanup**: Scheduled automatic cleanup of temporary files
- **Storage Monitoring**: Real-time storage usage tracking
- **Manual Controls**: On-demand data cleanup and reset
- **Progress Tracking**: Step-by-step verification progress monitoring

### 🔒 Security Features
- **Secure File Upload**: Validated file types and size limits
- **Temporary Storage**: Automatic cleanup of sensitive data
- **Session Management**: Secure conversation and context handling
- **Error Handling**: Comprehensive error handling and logging

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     Frontend Layer                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │   Chat   │  │  Camera  │  │  Upload  │  │   UI     │  │
│  │ Service  │  │ Service  │  │ Service  │  │Components│  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└──────────────────────────────────────────────────────────┘
                           ↕ HTTP/WebSocket
┌──────────────────────────────────────────────────────────┐
│                      API Layer (Flask)                   │
│  ┌────────────────────────────────────────────────────┐  │
│  │    REST Endpoints & WebSocket Handlers             │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
                           ↕
┌──────────────────────────────────────────────────────────┐
│                    Core Business Logic                   │
│  ┌────────────────────────────────────────────────────┐  │
│  │              LaosEKYCBot (Orchestrator)            │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
                           ↕
┌──────────────────────────────────────────────────────────┐
│                     Service Layer                        │
│  ┌─────────┐  ┌─────────┐  ┌────────────┐  ┌──────────┐  │
│  │   AI    │  │   OCR   │  │   Face     │  │ Cleanup  │  │
│  │ Service │  │ Service │  │Verification│  │ Service  │  │
│  └─────────┘  └─────────┘  └────────────┘  └──────────┘  │
└──────────────────────────────────────────────────────────┘
                           ↕
┌──────────────────────────────────────────────────────────┐
│                   External Services                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │
│  │   Gemini    │  │  OCR API    │  │  Face Verify    │   │
│  │  2.5 Flash  │  │  Server     │  │  WebSocket      │   │
│  └─────────────┘  └─────────────┘  └─────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

### Project Structure

```
Laos_Agent/
├── backend/                      # Backend application
│   ├── api/                      # API routes and endpoints
│   │   ├── __init__.py          # Application factory
│   │   └── routes.py            # Flask route definitions
│   ├── config/                   # Configuration management
│   │   ├── __init__.py          # Config exports
│   │   └── settings.py          # Environment settings
│   ├── core/                     # Core business logic
│   │   ├── __init__.py          # Core exports
│   │   └── bot.py               # Main orchestrator
│   ├── models/                   # Data models
│   │   ├── __init__.py          # Model exports
│   │   ├── conversation.py      # Chat models
│   │   └── verification.py      # Verification models
│   ├── services/                 # Business services
│   │   ├── __init__.py          # Service exports
│   │   ├── ai_service.py        # AI chatbot service
│   │   ├── ocr_service.py       # OCR processing
│   │   ├── face_verification_service.py  # Face verification
│   │   └── cleanup_service.py   # Data cleanup
│   └── utils/                    # Utility functions
│       └── formatters.py         # Data formatters
│
├── frontend/                     # Frontend application
│   ├── assets/                   # Static assets
│   │   ├── css/                  # Stylesheets
│   │   └── js/                   # JavaScript files
│   ├── components/               # UI components
│   └── index.html               # Main application page
│
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests
│   └── integration/              # Integration tests
│
├── docs/                         # Documentation
├── uploads/                      # Temporary uploads
├── main.py                       # Application entry point
├── run.py                        # Alternative run script
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## 🛠️ Technology Stack

### Backend
- **Python**: 3.11.5
- **Framework**: Flask 2.3.3
- **CORS**: Flask-CORS 4.0.0
- **HTTP Client**: Requests 2.31.0
- **WebSocket**: websockets 11.0.3, websocket-client 1.6.4
- **Environment**: python-dotenv 1.0.0
- **File Monitoring**: watchdog 2.3.0+

### Frontend
- **HTML5**: Modern semantic markup
- **CSS3**: Responsive design with custom styling
- **JavaScript**: Vanilla ES6+ (no framework dependencies)
- **WebSocket**: Real-time communication

### AI & External Services
- **AI Model**: Google Gemini 2.5 Flash Lite
- **OCR**: Custom OCR API integration
- **Face Verification**: WebSocket-based real-time verification service

### Development Tools
- **Testing**: pytest
- **Version Control**: Git
- **IDE Support**: VS Code, PyCharm

---

## ⚡ Quick Start

### Prerequisites

- Python 3.11.5 or higher
- pip package manager
- Webcam (for facial verification)
- Internet connection (for AI and OCR services)

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/PhucHuwu/Laos_Agent.git
cd Laos_Agent
```

#### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
# Copy from example (if available)
cp .env.example .env

# Or create manually
nano .env
```

Add the following configuration:

```env
# Application Settings
APP_NAME=Laos eKYC Agent
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
FLASK_DEBUG=False
FLASK_SECRET_KEY=your-secret-key-here-change-in-production

# AI API Configuration
API_KEY=your-gemini-api-key-here
API_URL=https://code.tinasoft.io/api/v1/chat/completions
MODEL=google/gemini-2.5-flash-lite

# OCR API Configuration
OCR_UPLOAD_URL=http://your-ocr-server:8000/api/v1/ocr/upload-image
OCR_SCAN_URL=http://your-ocr-server:8000/api/v1/ocr/scan-url
OCR_WEBSOCKET_URL=ws://your-ocr-server:8000/api/v1/ocr/ws/verify

# File Upload Settings
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
ALLOWED_EXTENSIONS=png,jpg,jpeg
```

#### 4. Run the Application

```bash
# Using main.py
python main.py

# Or using run.py
python run.py
```

#### 5. Access the Application

Open your browser and navigate to:

```
http://localhost:5001
```

You should see the eKYC verification interface!

---

## ⚙️ Configuration

### Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `APP_NAME` | Application name | Laos eKYC Agent | No |
| `FLASK_HOST` | Server host address | 0.0.0.0 | No |
| `FLASK_PORT` | Server port | 5001 | No |
| `FLASK_DEBUG` | Debug mode | False | No |
| `FLASK_SECRET_KEY` | Flask secret key | - | **Yes** |
| `API_KEY` | Gemini API key | - | **Yes** |
| `API_URL` | AI API endpoint | - | **Yes** |
| `MODEL` | AI model name | google/gemini-2.5-flash-lite | No |
| `OCR_UPLOAD_URL` | OCR upload endpoint | - | **Yes** |
| `OCR_SCAN_URL` | OCR scan endpoint | - | **Yes** |
| `OCR_WEBSOCKET_URL` | OCR WebSocket endpoint | - | **Yes** |
| `UPLOAD_FOLDER` | Upload directory | uploads | No |
| `MAX_CONTENT_LENGTH` | Max file size (bytes) | 16777216 (16MB) | No |
| `ALLOWED_EXTENSIONS` | Allowed file types | png,jpg,jpeg | No |

### Configuration Validation

The application automatically validates configuration on startup:

```bash
python main.py
```

If configuration is invalid, you'll see an error message:

```
❌ Configuration error: Missing required setting: API_KEY
Please check your .env file and ensure all required settings are configured.
```

---

## 📡 API Reference

### Chat Endpoints

#### POST /chat
Send a chat message and receive AI response.

**Request:**
```json
{
  "message": "ສະບາຍດີ"
}
```

**Response:**
```json
{
  "success": true,
  "response": "ສະບາຍດີ! ຂ້ອຍຈະຊ່ວຍທ່ານໃນການຢັ້ງຢືນຕົວຕົນ..."
}
```

#### POST /chat-stream
Send a chat message with streaming response.

**Request:**
```json
{
  "message": "ຊ່ວຍຂ້ອຍດ້ວຍ"
}
```

**Response:** Server-Sent Events (SSE)
```
data: {"type": "thinking", "content": "ກຳລັງຄິດ..."}

data: {"type": "content", "content": "ແນ່ນອນ..."}

data: [DONE]
```

#### POST /reset
Reset conversation history.

**Response:**
```json
{
  "success": true,
  "message": "ໄດ້ reset ການສົນທະນາແລ້ວ"
}
```

### File Upload Endpoints

#### POST /upload
Upload and process ID card image.

**Request:** multipart/form-data
- `file`: Image file (PNG, JPG, JPEG)

**Response:**
```json
{
  "success": true,
  "image_url": "http://...",
  "scan_result": {
    "id": "...",
    "name": "...",
    "dob": "...",
    "address": "..."
  },
  "formatted_html": "<div>...</div>",
  "message": "ອັບໂຫຼດ ແລະ ສະແກນສຳເລັດ!"
}
```

### Face Verification Endpoints

#### POST /verify-face
Batch face verification.

**Request:**
```json
{
  "id_card_image_url": "http://...",
  "selfie_image_url": "http://..."
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "same_person": true,
    "similarity": 0.95,
    "status": "success"
  }
}
```

#### POST /verify-face-realtime
Real-time face verification.

**Request/Response:** Same as `/verify-face`

#### POST /start-websocket-verification
Initialize WebSocket verification session.

**Request:**
```json
{
  "id_card_image_url": "http://..."
}
```

**Response:**
```json
{
  "success": true,
  "message": "ເລີ່ມການຢັ້ງຢືນ WebSocket ສຳເລັດແລ້ວ"
}
```

#### POST /send-frame
Send frame for real-time verification.

**Request:**
```json
{
  "frame_base64": "data:image/jpeg;base64,..."
}
```

**Response:**
```json
{
  "success": true,
  "message": "ສົ່ງ frame ສຳເລັດແລ້ວ",
  "result": {
    "same_person": true,
    "similarity": 0.92,
    "bbox": [x, y, w, h]
  }
}
```

#### POST /stop-websocket-verification
Stop WebSocket verification.

**Response:**
```json
{
  "success": true,
  "message": "ຢຸດການຢັ້ງຢືນ WebSocket ແລ້ວ"
}
```

### Data Management Endpoints

#### POST /cleanup
Manual cleanup of eKYC data.

**Response:**
```json
{
  "success": true,
  "message": "ລ້າງຂໍ້ມູນສຳເລັດ"
}
```

#### POST /reset-all
Reset all data and files.

**Response:**
```json
{
  "success": true,
  "message": "Reset ທັງໝົດສຳເລັດ"
}
```

#### GET /storage-info
Get storage information.

**Response:**
```json
{
  "upload_folder": "uploads",
  "files_count": 5,
  "total_size": 1234567
}
```

#### POST /schedule-cleanup
Schedule automatic cleanup.

**Request:**
```json
{
  "delay_seconds": 30
}
```

**Response:**
```json
{
  "success": true,
  "message": "ກຳນົດເວລາລ້າງຂໍ້ມູນສຳເລັດ"
}
```

### Debug Endpoints

#### GET /
Main application page.

#### GET /debug
Application debug information.

**Response:**
```json
{
  "static_folder": "/path/to/static",
  "static_url_path": "/static",
  "css_exists": true,
  "css_path": "/path/to/css/style.css"
}
```

---

## 📚 Module Documentation

### Backend Modules

#### Configuration Management (`backend/config/`)

**settings.py**: Centralized configuration management
- Loads settings from environment variables
- Provides validation and default values
- Exports singleton `settings` instance

```python
from backend.config import settings

print(settings.FLASK_PORT)  # 5001
print(settings.API_KEY)     # your-api-key
```

#### Data Models (`backend/models/`)

**conversation.py**: Chat conversation models
- `Message`: Individual message in conversation
- `Conversation`: Manages conversation history and context
- Progress tracking and context management

**verification.py**: Verification data models
- `ScanResult`: OCR scan results
- `VerificationResult`: Face verification results

#### Service Layer (`backend/services/`)

**ai_service.py**: AI chatbot service
- Streaming chat responses with thinking/reasoning
- Tool call management and execution
- Conversation history management
- Integration with Gemini 2.5 Flash Lite

**ocr_service.py**: OCR document processing
- Image upload and processing
- Data extraction from ID cards
- URL-based and file-based scanning

**face_verification_service.py**: Facial verification
- Batch verification (single image comparison)
- Real-time verification (WebSocket streaming)
- Similarity scoring and confidence metrics

**cleanup_service.py**: Data cleanup service
- Automatic cleanup scheduling
- Manual cleanup triggers
- Storage monitoring and management

#### Core Business Logic (`backend/core/`)

**bot.py**: Main orchestrator (`LaosEKYCBot`)
- Coordinates all services
- Manages conversation flow
- Handles tool calls and responses
- Progress tracking and state management

#### API Layer (`backend/api/`)

**routes.py**: Flask routes and endpoints
- REST API definitions
- WebSocket handlers
- File upload handling
- Error handling and responses

**__init__.py**: Application factory
- Creates and configures Flask app
- Registers routes and middleware
- Sets up CORS and static files

### Frontend Structure

**index.html**: Main application page
- Chat interface
- File upload UI
- Camera modal for face verification
- Result display components

**assets/css/**: Stylesheets
- Responsive design
- Custom components styling
- Mobile-friendly layout

**assets/js/**: JavaScript modules
- API communication
- Chat handling
- Camera operations
- WebSocket management

---

## 💻 Development Guide

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/PhucHuwu/Laos_Agent.git
cd Laos_Agent

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8

# Create .env file
cp .env.example .env
# Edit .env with your configuration

# Run in debug mode
export FLASK_DEBUG=True  # On Windows: set FLASK_DEBUG=True
python main.py
```

### Code Architecture Principles

1. **Separation of Concerns**
   - Each module has a single, well-defined responsibility
   - Clear boundaries between layers (API, Core, Services, Models)

2. **Dependency Injection**
   - Services are injected into core modules
   - Loose coupling between components
   - Easy to test and mock

3. **Configuration Management**
   - Centralized configuration in `backend/config/settings.py`
   - Environment-based configuration
   - Validation on startup

4. **Error Handling**
   - Consistent error handling patterns
   - Meaningful error messages in Lao language
   - Proper HTTP status codes

5. **Testing**
   - Unit tests for individual components
   - Integration tests for API endpoints
   - Test coverage tracking

### Adding New Features

#### Backend Feature

1. **Add Model** (if needed)
```python
# backend/models/new_feature.py
class NewFeatureModel:
    def __init__(self, data):
        self.data = data
```

2. **Add Service**
```python
# backend/services/new_feature_service.py
class NewFeatureService:
    def __init__(self, config):
        self.config = config
    
    def process(self, data):
        # Implementation
        pass
```

3. **Update Core Bot**
```python
# backend/core/bot.py
from backend.services.new_feature_service import NewFeatureService

class LaosEKYCBot:
    def __init__(self):
        # ...
        self.new_feature_service = NewFeatureService(settings)
```

4. **Add API Route**
```python
# backend/api/routes.py
@app.route('/new-feature', methods=['POST'])
def new_feature():
    data = request.get_json()
    result = bot.new_feature_service.process(data)
    return jsonify(result)
```

5. **Add Tests**
```python
# tests/unit/test_new_feature.py
def test_new_feature():
    service = NewFeatureService(mock_config)
    result = service.process(test_data)
    assert result['success'] == True
```

#### Frontend Feature

1. **Add HTML Component**
```html
<!-- frontend/index.html -->
<div id="new-feature">
    <!-- Component markup -->
</div>
```

2. **Add Styling**
```css
/* frontend/assets/css/style.css */
#new-feature {
    /* Styles */
}
```

3. **Add JavaScript**
```javascript
// frontend/assets/js/main.js
async function handleNewFeature(data) {
    const response = await fetch('/new-feature', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
    return await response.json();
}
```

### Code Style Standards

- **Python**: Follow PEP 8 guidelines
- **Type Hints**: Use type hints for function parameters and return values
- **Docstrings**: Document all classes and functions
- **Comments**: Add comments for complex logic
- **Naming**: Use descriptive variable and function names
  - Classes: `PascalCase`
  - Functions: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes
git add .
git commit -m "feat: Add new feature"

# Push to remote
git push origin feature/new-feature

# Create pull request on GitHub
```

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest tests/unit/test_models.py

# Run with verbose output
pytest -v

# Run specific test
pytest tests/unit/test_models.py::test_conversation_model
```

### Test Structure

```
tests/
├── unit/                    # Unit tests
│   ├── test_models.py      # Model tests
│   ├── test_services.py    # Service tests
│   └── test_utils.py       # Utility tests
│
└── integration/             # Integration tests
    ├── test_api.py         # API endpoint tests
    └── test_workflows.py   # End-to-end workflow tests
```

### Writing Tests

```python
# tests/unit/test_new_service.py
import pytest
from backend.services.new_service import NewService

@pytest.fixture
def service():
    return NewService(mock_config)

def test_service_process(service):
    result = service.process(test_data)
    assert result['success'] == True
    assert result['data'] is not None

def test_service_error_handling(service):
    with pytest.raises(ValueError):
        service.process(invalid_data)
```

---

## 🚢 Deployment

### Production Deployment

#### Using Gunicorn (Recommended)

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 "backend.api:create_app()"
```

#### Using Docker

```dockerfile
# Dockerfile
FROM python:3.11.5-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "backend.api:create_app()"]
```

```bash
# Build and run
docker build -t laos-ekyc .
docker run -p 5001:5001 --env-file .env laos-ekyc
```

#### Using Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5001:5001"
    env_file:
      - .env
    volumes:
      - ./uploads:/app/uploads
    restart: unless-stopped
```

```bash
# Run with Docker Compose
docker-compose up -d
```

### Environment-Specific Configuration

#### Development
```env
FLASK_DEBUG=True
FLASK_HOST=127.0.0.1
```

#### Production
```env
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_SECRET_KEY=<strong-random-key>
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/app/frontend/assets;
    }
}
```

---

## 🔒 Security Considerations

### Best Practices

1. **API Keys**: Never commit API keys to version control
   - Use environment variables
   - Use secret management services in production

2. **File Upload Security**
   - Validate file types and sizes
   - Scan uploaded files for malware
   - Use secure filename generation
   - Clean up temporary files

3. **Session Security**
   - Use strong secret keys
   - Enable HTTPS in production
   - Set secure cookie flags

4. **Data Privacy**
   - Implement automatic data cleanup
   - Encrypt sensitive data at rest
   - Use secure connections for external services

5. **Input Validation**
   - Validate all user inputs
   - Sanitize data before processing
   - Use parameterized queries (if using database)

6. **Error Handling**
   - Don't expose sensitive information in error messages
   - Log errors securely
   - Use appropriate HTTP status codes

### Security Checklist

- [ ] Change default `FLASK_SECRET_KEY`
- [ ] Enable HTTPS in production
- [ ] Set `FLASK_DEBUG=False` in production
- [ ] Implement rate limiting
- [ ] Add authentication/authorization (if needed)
- [ ] Regular security audits
- [ ] Keep dependencies updated
- [ ] Implement logging and monitoring
- [ ] Configure firewall rules
- [ ] Regular backups

---

## 🔧 Troubleshooting

### Common Issues

#### Issue: Application won't start

**Error**: `Configuration error: Missing required setting: API_KEY`

**Solution**:
```bash
# Check .env file exists
ls -la .env

# Verify .env contains API_KEY
cat .env | grep API_KEY

# Set API_KEY if missing
echo "API_KEY=your-key-here" >> .env
```

#### Issue: Port already in use

**Error**: `Address already in use: 5001`

**Solution**:
```bash
# Find process using port
lsof -i :5001

# Kill the process
kill -9 <PID>

# Or use different port
export FLASK_PORT=5002
python main.py
```

#### Issue: OCR/Face verification not working

**Error**: `Connection refused` or `Timeout`

**Solution**:
- Verify OCR service is running
- Check OCR_*_URL configuration
- Test connectivity: `curl http://ocr-server:8000/health`
- Check firewall settings

#### Issue: File upload fails

**Error**: `File too large` or `Invalid file type`

**Solution**:
- Check file size < 16MB
- Verify file type is PNG, JPG, or JPEG
- Check `UPLOAD_FOLDER` exists and is writable

#### Issue: WebSocket connection fails

**Error**: `WebSocket connection failed`

**Solution**:
- Verify `OCR_WEBSOCKET_URL` is correct
- Check WebSocket server is running
- Test WebSocket connectivity
- Check firewall allows WebSocket connections

### Debug Mode

Enable debug mode for detailed error messages:

```bash
export FLASK_DEBUG=True
python main.py
```

### Logging

Check application logs:

```bash
# View logs in console
python main.py

# Redirect to file
python main.py > app.log 2>&1

# Tail logs in real-time
tail -f app.log
```

---

## 👥 Contributing

We welcome contributions! Please follow these guidelines:

### How to Contribute

1. **Fork the Repository**
   ```bash
   git clone https://github.com/your-username/Laos_Agent.git
   cd Laos_Agent
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make Your Changes**
   - Follow code style standards
   - Add tests for new features
   - Update documentation

4. **Run Tests**
   ```bash
   pytest
   ```

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: Add amazing feature"
   ```

6. **Push to Your Fork**
   ```bash
   git push origin feature/amazing-feature
   ```

7. **Create a Pull Request**
   - Go to GitHub
   - Click "New Pull Request"
   - Describe your changes
   - Submit for review

### Commit Message Guidelines

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Examples:
```
feat: Add real-time face verification
fix: Resolve WebSocket connection issue
docs: Update API reference
```

### Code Review Process

1. Submit pull request
2. Automated tests run
3. Code review by maintainers
4. Address feedback
5. Merge upon approval

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support & Contact

### Technical Support

For technical support and questions:

- 📧 Email: support@example.com
- 💬 Discord: [Join our server](#)
- 📝 Issues: [GitHub Issues](https://github.com/PhucHuwu/Laos_Agent/issues)

### Documentation

- 📖 [Full Documentation](docs/)
- 🎓 [User Guide](docs/user-guide.md)
- 🔧 [Developer Guide](docs/developer-guide.md)
- 📡 [API Reference](docs/api-reference.md)

---

## 🙏 Acknowledgments

- Google Gemini for AI capabilities
- Flask community for excellent web framework
- OCR service providers
- All contributors and supporters

---

<div align="center">

### ⭐ If you find this project helpful, please consider giving it a star!

Made with ❤️ for the Lao community

[Report Bug](https://github.com/PhucHuwu/Laos_Agent/issues) • [Request Feature](https://github.com/PhucHuwu/Laos_Agent/issues) • [View Demo](#)

</div>
