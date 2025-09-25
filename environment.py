#!/usr/bin/env python3
"""
Environment configuration file
Load this to set all environment variables from .env file
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Verify that required environment variables are loaded
required_vars = [
    "GEMINI_API_KEY",
    "GEMINI_MODEL", 
    "MYSQL_HOST",
    "MYSQL_PORT",
    "MYSQL_USER",
    "MYSQL_PASSWORD",
    "MYSQL_DATABASE",
    "SECRET_KEY",
    "ACCESS_TOKEN_EXPIRE_MINUTES"
]

missing_vars = []
for var in required_vars:
    if os.getenv(var) is None:
        missing_vars.append(var)

if missing_vars:
    print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
    print("Please check your .env file and ensure all required variables are set.")
    exit(1)

print("✅ Environment variables loaded successfully!")
print(f"GEMINI_API_KEY: {'*' * 20}...{os.environ['GEMINI_API_KEY'][-4:]}")
print(f"GEMINI_MODEL: {os.environ['GEMINI_MODEL']}")
