# Hệ thống eKYC Căn cước công dân Lào

Hệ thống định danh điện tử (eKYC) hỗ trợ xác thực căn cước công dân Lào sử dụng AI và xác thực khuôn mặt real-time.

## 🏗️ Cấu trúc dự án

```
Laos_Agent/
├── backend/                    # Backend modules
│   ├── api/                   # Flask API routes
│   ├── config/                # Configuration management
│   ├── core/                  # Core business logic
│   ├── models/                # Data models
│   └── services/              # Business services
├── frontend/                   # Frontend modules
│   ├── assets/                # Static assets (CSS, JS, images)
│   ├── components/            # UI components
│   ├── services/              # Frontend services
│   └── utils/                 # Utility functions
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests
│   └── integration/           # Integration tests
├── docs/                      # Documentation
├── uploads/                   # File upload directory
├── main.py                    # Application entry point
└── requirements.txt           # Python dependencies
```

## 🚀 Cài đặt và chạy

### Yêu cầu hệ thống

- Python 3.8+
- pip
- Webcam (cho xác thực khuôn mặt)

### Cài đặt

1. **Clone repository:**
```bash
git clone <repository-url>
cd Laos_Agent
```

2. **Cài đặt dependencies:**
```bash
pip install -r requirements.txt
```

3. **Cấu hình environment:**
```bash
cp .env.example .env
# Chỉnh sửa .env với API keys và cấu hình của bạn
```

4. **Chạy ứng dụng:**
```bash
python main.py
```

Hoặc sử dụng script run.py:
```bash
python run.py
```

### Truy cập ứng dụng

Mở trình duyệt và truy cập: `http://localhost:5001`

## ⚙️ Cấu hình

### File .env

```env
# API Configuration
API_KEY=your-api-key-here
API_URL=https://code.tinasoft.io/api/v1/chat/completions
MODEL=google/gemini-2.5-flash-lite

# OCR API Configuration
OCR_UPLOAD_URL=http://172.16.12.136:8000/api/v1/ocr/upload-image
OCR_SCAN_URL=http://172.16.12.136:8000/api/v1/ocr/scan-url
OCR_WEBSOCKET_URL=ws://127.0.0.1:8000/api/v1/ocr/ws/verify

# Flask Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
FLASK_DEBUG=False
FLASK_SECRET_KEY=your-secret-key-here

# Upload Configuration
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216  # 16MB
```

## 🧪 Testing

### Chạy unit tests:
```bash
python -m pytest tests/unit/ -v
```

### Chạy integration tests:
```bash
python -m pytest tests/integration/ -v
```

### Chạy tất cả tests:
```bash
python -m pytest tests/ -v
```

## 📁 Mô tả modules

### Backend

#### `backend/config/`
- **settings.py**: Quản lý cấu hình ứng dụng từ environment variables
- **__init__.py**: Export settings instance

#### `backend/models/`
- **conversation.py**: Models cho chat conversation và messages
- **verification.py**: Models cho kết quả OCR scan và face verification
- **__init__.py**: Export tất cả models

#### `backend/services/`
- **ai_service.py**: Service xử lý AI chatbot và tool calls
- **ocr_service.py**: Service xử lý OCR upload và scan
- **face_verification_service.py**: Service xử lý face verification
- **__init__.py**: Export tất cả services

#### `backend/core/`
- **bot.py**: Main bot class orchestrate tất cả services
- **__init__.py**: Export bot class

#### `backend/api/`
- **routes.py**: Flask routes và API endpoints
- **__init__.py**: Export create_app function

### Frontend

#### `frontend/services/`
- **api_service.py**: Service giao tiếp với backend API
- **chat_service.py**: Service xử lý chat functionality
- **camera_service.py**: Service xử lý camera operations
- **websocket_service.py**: Service xử lý WebSocket real-time
- **__init__.py**: Export tất cả services

#### `frontend/utils/`
- **formatters.py**: Utilities format data (file size, scan results, etc.)
- **validators.py**: Utilities validate input data
- **__init__.py**: Export utilities

#### `frontend/assets/`
- **css/style.css**: Stylesheet chính
- **js/main.js**: JavaScript chính (sẽ được refactor)

### Tests

#### `tests/unit/`
- **test_models.py**: Unit tests cho data models

#### `tests/integration/`
- **test_api.py**: Integration tests cho API endpoints

## 🔧 API Endpoints

### Chat
- `POST /chat` - Gửi tin nhắn chat
- `POST /reset` - Reset conversation

### File Upload
- `POST /upload` - Upload file ảnh

### Face Verification
- `POST /verify-face` - Xác thực khuôn mặt batch
- `POST /verify-face-realtime` - Xác thực khuôn mặt real-time
- `POST /start-websocket-verification` - Bắt đầu WebSocket verification
- `POST /send-frame` - Gửi frame cho real-time verification
- `POST /stop-websocket-verification` - Dừng WebSocket verification

### Debug
- `GET /debug` - Debug information
- `GET /` - Main page

## 🛠️ Development

### Cấu trúc code

1. **Separation of Concerns**: Mỗi module có trách nhiệm riêng biệt
2. **Dependency Injection**: Services được inject vào core modules
3. **Configuration Management**: Tất cả config được quản lý tập trung
4. **Error Handling**: Xử lý lỗi consistent across modules
5. **Testing**: Unit và integration tests cho tất cả modules

### Thêm features mới

1. **Backend**: Thêm service mới trong `backend/services/`, tạo models trong `backend/models/`
2. **Frontend**: Thêm service mới trong `frontend/services/`, components trong `frontend/components/`
3. **API**: Thêm routes mới trong `backend/api/routes.py`
4. **Tests**: Thêm tests tương ứng trong `tests/`

### Code Style

- Sử dụng type hints
- Docstrings cho tất cả functions/classes
- Error handling với try/catch
- Consistent naming conventions

## 📝 License

MIT License

## 🤝 Contributing

1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Tạo Pull Request

## 📞 Support

Liên hệ team development để được hỗ trợ.
