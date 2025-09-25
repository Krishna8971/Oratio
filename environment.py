#!/usr/bin/env python3
"""
Environment configuration file
Load this to set all environment variables
"""

import os

# Set environment variables
os.environ["GEMINI_API_KEY"] = "AIzaSyCxrA2E-qBw0IPjeWhFdNHw9ti-x5CB7FY"
os.environ["GEMINI_MODEL"] = "gemini-1.5-flash"

# MySQL Database Configuration
os.environ["MYSQL_HOST"] = "localhost"
os.environ["MYSQL_PORT"] = "3306"
os.environ["MYSQL_USER"] = "root"
os.environ["MYSQL_PASSWORD"] = ""
os.environ["MYSQL_DATABASE"] = "oratio"

# Security
os.environ["SECRET_KEY"] = "your-secret-key-change-in-production"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"

print("✅ Environment variables loaded successfully!")
print(f"GEMINI_API_KEY: {'*' * 20}...{os.environ['GEMINI_API_KEY'][-4:]}")
print(f"GEMINI_MODEL: {os.environ['GEMINI_MODEL']}")
