# Laos eKYC Agent

An AI-powered eKYC (Electronic Know Your Customer) chatbot system for Laos, featuring document verification and identity authentication capabilities.

## Tech Stack

### Backend

-   **Framework**: FastAPI
-   **Language**: Python 3.10+
-   **Key Libraries**: uvicorn, httpx, websockets, pydantic

### Frontend

-   **Framework**: Next.js 16
-   **Language**: TypeScript
-   **UI Libraries**: Radix UI, TailwindCSS, Lucide React

## Project Structure

```
Laos_Agent/
├── backend/           # FastAPI backend server
│   ├── app/           # Main application code
│   ├── api/           # API routes
│   ├── config/        # Configuration files
│   ├── models/        # Data models
│   ├── services/      # Business logic services
│   └── utils/         # Utility functions
└── frontend/          # Next.js frontend application
    ├── app/           # Next.js app router pages
    ├── components/    # React components
    ├── hooks/         # Custom React hooks
    └── lib/           # Utility libraries
```

## Installation

### Prerequisites

-   Python 3.10+
-   Node.js 18+
-   npm or pnpm

### Backend Setup

1. Navigate to the backend directory:

    ```bash
    cd backend
    ```

2. Create a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Copy the environment file and configure:

    ```bash
    cp .env.example .env
    ```

5. Update `.env` with your API keys and configuration.

6. Start the backend server:
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 3724
    ```

### Frontend Setup

1. Navigate to the frontend directory:

    ```bash
    cd frontend
    ```

2. Install dependencies:

    ```bash
    npm install
    ```

3. Start the development server:

    ```bash
    npm run dev
    ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Environment Variables

See `backend/.env.example` for required environment variables:

| Variable            | Description                         |
| ------------------- | ----------------------------------- |
| `API_KEY`           | OpenRouter API key for AI services  |
| `API_URL`           | AI API endpoint URL                 |
| `MODEL`             | AI model to use                     |
| `OCR_UPLOAD_URL`    | OCR service upload endpoint         |
| `OCR_SCAN_URL`      | OCR service scan endpoint           |
| `OCR_WEBSOCKET_URL` | OCR WebSocket verification endpoint |
| `SECRET_KEY`        | Application secret key              |

## License

This project is proprietary software.
