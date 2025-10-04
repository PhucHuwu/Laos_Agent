#!/usr/bin/env python3
"""
Script để chạy hệ thống eKYC Căn cước công dân Lào
"""

import os
import sys
import subprocess


def check_requirements():
    """Kiểm tra và cài đặt requirements"""
    try:
        import flask
        import flask_cors
        import requests
        import dotenv
        print("✅ Tất cả dependencies đã được cài đặt")
        return True
    except ImportError as e:
        print(f"❌ Thiếu dependency: {e}")
        print("Đang cài đặt requirements...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Đã cài đặt thành công requirements")
            return True
        except subprocess.CalledProcessError:
            print("❌ Không thể cài đặt requirements")
            return False


def check_env_file():
    """Kiểm tra file .env"""
    if not os.path.exists('.env'):
        print("⚠️  File .env không tồn tại")
        print("Tạo file .env mẫu...")
        with open('.env', 'w', encoding='utf-8') as f:
            f.write("API_KEY=your-api-key-here\n")
        print("✅ Đã tạo file .env mẫu. Vui lòng cập nhật API_KEY")
        return False
    else:
        print("✅ File .env đã tồn tại")
        return True


def create_uploads_folder():
    """Tạo thư mục uploads"""
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
        print("✅ Đã tạo thư mục uploads")
    else:
        print("✅ Thư mục uploads đã tồn tại")


def main():
    """Hàm main"""
    print("🚀 Khởi động Hệ thống eKYC Căn cước công dân Lào")
    print("=" * 50)

    # Kiểm tra requirements
    if not check_requirements():
        return

    # Kiểm tra file .env
    env_ok = check_env_file()

    # Tạo thư mục uploads
    create_uploads_folder()

    print("\n" + "=" * 50)

    if not env_ok:
        print("⚠️  Vui lòng cập nhật API_KEY trong file .env trước khi chạy")
        print("Sau đó chạy lại script này")
        return

    print("🎉 Hệ thống đã sẵn sàng!")
    print("🌐 Truy cập: http://localhost:5001")
    print("📱 Hoặc: http://0.0.0.0:5001")
    print("\nNhấn Ctrl+C để dừng server")
    print("=" * 50)

    # Chạy Flask app
    try:
        from backend.api import create_app
        app = create_app()
        app.run(debug=True, host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        print("\n👋 Tạm biệt!")
    except Exception as e:
        print(f"❌ Lỗi: {e}")


if __name__ == "__main__":
    main()
