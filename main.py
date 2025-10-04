#!/usr/bin/env python3
"""
Main application entry point for Laos eKYC Agent
"""

import os
import sys
from backend.api import create_app
from backend.config import settings

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Main application entry point"""

    # Validate settings
    try:
        settings.validate()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("Please check your .env file and ensure all required settings are configured.")
        return 1

    # Create Flask app
    app = create_app()

    print(f"🚀 Starting {settings.APP_NAME}")
    print(f"🌐 Server will be available at: http://{settings.FLASK_HOST}:{settings.FLASK_PORT}")
    print(f"🔧 Debug mode: {'ON' if settings.FLASK_DEBUG else 'OFF'}")
    print("=" * 60)

    try:
        # Run the application
        app.run(
            host=settings.FLASK_HOST,
            port=settings.FLASK_PORT,
            debug=settings.FLASK_DEBUG
        )
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Application error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
