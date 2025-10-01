#!/usr/bin/env python3
"""
Development environment setup script for NSC International.
This script sets up the development environment with all necessary tools.
"""

import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False


def main():
    """Main setup function."""
    print("🚀 Setting up NSC International development environment...")

    # Check if we're in the right directory
    if not Path("manage.py").exists():
        print(
            "❌ Error: manage.py not found. Please run this script from the project root."
        )
        sys.exit(1)

    # Install development dependencies
    commands = [
        ("pip install --upgrade pip", "Upgrading pip"),
        ("pip install -r requirements.txt", "Installing project dependencies"),
        ("pip install -r requirements-security.txt", "Installing security tools"),
        (
            "pip install black isort flake8 mypy pre-commit",
            "Installing code quality tools",
        ),
    ]

    success_count = 0
    for command, description in commands:
        if run_command(command, description):
            success_count += 1

    # Setup pre-commit hooks
    if run_command("pre-commit install", "Installing pre-commit hooks"):
        success_count += 1

    # Run initial code formatting
    if run_command("black .", "Running initial code formatting"):
        success_count += 1

    if run_command("isort .", "Running initial import sorting"):
        success_count += 1

    # Run security checks
    if run_command("python -m safety check", "Running safety check"):
        success_count += 1

    if run_command(
        "python -m bandit -r . --skip B101,B601", "Running bandit security scan"
    ):
        success_count += 1

    # Run Django checks
    if run_command("python manage.py check", "Running Django system check"):
        success_count += 1

    if run_command("python manage.py test", "Running Django tests"):
        success_count += 1

    print(f"\n🎉 Setup completed! {success_count}/{len(commands) + 6} tasks successful")

    if success_count == len(commands) + 6:
        print("✅ All tasks completed successfully!")
        print("\n📋 Next steps:")
        print("1. Create a superuser: python manage.py createsuperuser")
        print("2. Run migrations: python manage.py migrate")
        print("3. Start development server: python manage.py runserver")
        print("4. Install pre-commit hooks: pre-commit install")
    else:
        print("⚠️  Some tasks failed. Please check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
