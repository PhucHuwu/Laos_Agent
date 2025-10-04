#!/usr/bin/env python3
"""
Script to run tests for Laos eKYC Agent
"""

import sys
import subprocess
import os


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print('='*60)

    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with exit code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def main():
    """Main test runner"""
    print("🧪 Running tests for Laos eKYC Agent")
    print("="*60)

    # Check if pytest is installed
    try:
        import pytest
        print("✅ pytest is available")
    except ImportError:
        print("❌ pytest not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pytest"])
        print("✅ pytest installed")

    # Change to project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Run different types of tests
    test_commands = [
        ("python -m pytest tests/unit/ -v", "Unit Tests"),
        ("python -m pytest tests/integration/ -v", "Integration Tests"),
        ("python -m pytest tests/ -v --tb=short", "All Tests (Summary)"),
        ("python -m pytest tests/ -v --cov=backend --cov-report=html", "Tests with Coverage")
    ]

    success_count = 0
    total_count = len(test_commands)

    for command, description in test_commands:
        if run_command(command, description):
            success_count += 1
        else:
            print(f"⚠️  {description} failed")

    # Summary
    print(f"\n{'='*60}")
    print("📊 Test Summary")
    print('='*60)
    print(f"✅ Successful: {success_count}/{total_count}")
    print(f"❌ Failed: {total_count - success_count}/{total_count}")

    if success_count == total_count:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
