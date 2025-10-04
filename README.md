# Laos eKYC Identity Verification System

A comprehensive electronic Know Your Customer (eKYC) system for Laotian citizen identity verification using AI-powered chatbot technology, OCR document scanning, and real-time facial recognition.

## Project Architecture

```
Laos_Agent/
├── backend/                   # Backend application modules
│   ├── api/                   # Flask API routes and endpoints
│   ├── config/                # Configuration management
│   ├── core/                  # Core business logic orchestration
│   ├── models/                # Data models and schemas
│   └── services/              # Business service layer
│
├── frontend/                  # Frontend application modules
│   ├── assets/                # Static assets (CSS, JS, images)
│   ├── components/            # Reusable UI components
│   ├── services/              # Frontend service layer
│   └── utils/                 # Utility functions
│
├── tests/                     # Comprehensive test suite
│   ├── unit/                  # Unit tests
│   └── integration/           # Integration tests
│
├── docs/                      # Project documentation
├── uploads/                   # Temporary file upload directory
├── main.py                    # Application entry point
└── requirements.txt           # Python dependencies
```

## Installation and Setup

### System Requirements

- Python 3.8 or higher
- pip package manager
- Webcam for facial verification functionality

### Installation Steps

1. **Clone the repository:**
```bash
git clone <repository-url>
cd Laos_Agent
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration settings
```

4. **Run the application:**
```bash
python main.py
```

Alternatively, use the run script:
```bash
python run.py
```

### Accessing the Application

Open your web browser and navigate to: `http://localhost:5001`

## Configuration

### Environment Variables

```env
# AI API Configuration
API_KEY=your-api-key-here
API_URL=https://code.tinasoft.io/api/v1/chat/completions
MODEL=google/gemini-2.5-flash-lite

# OCR API Configuration
OCR_UPLOAD_URL=http://172.16.12.136:8000/api/v1/ocr/upload-image
OCR_SCAN_URL=http://172.16.12.136:8000/api/v1/ocr/scan-url
OCR_WEBSOCKET_URL=ws://127.0.0.1:8000/api/v1/ocr/ws/verify

# Flask Application Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
FLASK_DEBUG=False
FLASK_SECRET_KEY=your-secret-key-here

# File Upload Configuration
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216  # 16MB
```

## Testing

### Running Unit Tests
```bash
python -m pytest tests/unit/ -v
```

### Running Integration Tests
```bash
python -m pytest tests/integration/ -v
```

### Running All Tests
```bash
python -m pytest tests/ -v
```

## Module Documentation

### Backend Modules

#### Configuration Management (`backend/config/`)
- **settings.py**: Centralized application configuration management from environment variables
- **__init__.py**: Exports settings instance for application-wide access

#### Data Models (`backend/models/`)
- **conversation.py**: Data models for chat conversations and message handling
- **verification.py**: Models for OCR scan results and facial verification data
- **__init__.py**: Exports all model classes

#### Service Layer (`backend/services/`)
- **ai_service.py**: AI chatbot service with tool call management and conversation handling
- **ocr_service.py**: OCR document processing service for image upload and data extraction
- **face_verification_service.py**: Facial verification service supporting both batch and real-time modes
- **__init__.py**: Exports all service classes

#### Core Business Logic (`backend/core/`)
- **bot.py**: Main orchestrator class that coordinates all services and handles tool calls
- **__init__.py**: Exports bot class

#### API Layer (`backend/api/`)
- **routes.py**: Flask routes and REST API endpoints
- **__init__.py**: Exports application factory function

### Frontend Modules

#### Service Layer (`frontend/services/`)
- **api_service.js**: Service for backend API communication
- **chat_service.js**: Chat functionality and message handling
- **camera_service.js**: Camera operations and media stream management
- **websocket_service.js**: Real-time WebSocket communication service
- **__init__.py**: Exports all service modules

#### Utility Functions (`frontend/utils/`)
- **formatters.js**: Data formatting utilities (file sizes, scan results, etc.)
- **validators.js**: Input validation utilities
- **__init__.py**: Exports utility functions

#### Static Assets (`frontend/assets/`)
- **css/style.css**: Main application stylesheet
- **js/main.js**: Primary JavaScript application logic (pending refactoring)

### Test Suite

#### Unit Tests (`tests/unit/`)
- **test_models.py**: Unit tests for data models and validation

#### Integration Tests (`tests/integration/`)
- **test_api.py**: Integration tests for API endpoints and workflows

## API Reference

### Chat Endpoints
- `POST /chat` - Send chat message and receive AI response
- `POST /reset` - Reset conversation history

### File Upload Endpoints
- `POST /upload` - Upload image file for processing

### Facial Verification Endpoints
- `POST /verify-face` - Batch facial verification
- `POST /verify-face-realtime` - Real-time facial verification
- `POST /start-websocket-verification` - Initialize WebSocket verification session
- `POST /send-frame` - Send frame data for real-time verification
- `POST /stop-websocket-verification` - Terminate WebSocket verification session

### Debug Endpoints
- `GET /debug` - Application debug information
- `GET /` - Main application page

## Development Guidelines

### Code Architecture Principles

1. **Separation of Concerns**: Each module maintains distinct responsibilities
2. **Dependency Injection**: Services are injected into core modules for loose coupling
3. **Configuration Management**: Centralized configuration handling across all modules
4. **Error Handling**: Consistent error handling patterns throughout the application
5. **Testing**: Comprehensive unit and integration test coverage for all modules

### Adding New Features

1. **Backend Development**: Add new services in `backend/services/`, create corresponding models in `backend/models/`
2. **Frontend Development**: Add new services in `frontend/services/`, create components in `frontend/components/`
3. **API Development**: Add new routes in `backend/api/routes.py`
4. **Testing**: Add corresponding tests in the `tests/` directory

### Code Style Standards

- Use type hints for all function parameters and return values
- Include comprehensive docstrings for all functions and classes
- Implement proper error handling with try/catch blocks
- Follow consistent naming conventions throughout the codebase

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to your branch
5. Create a Pull Request

## Support

For technical support and questions, please contact the development team.
