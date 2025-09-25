#!/usr/bin/env python3
"""
Database setup script for Oratio Backend
Creates the MySQL database and tables
"""

import os
import pymysql
from config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

def create_database():
    """Create the MySQL database if it doesn't exist"""
    try:
        # Connect to MySQL server (without specifying database)
        connection = pymysql.connect(
            host=MYSQL_HOST,
            port=int(MYSQL_PORT),
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE}")
            print(f"✅ Database '{MYSQL_DATABASE}' created or already exists")
            
        connection.close()
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        print("\nPlease make sure:")
        print("1. MySQL server is running")
        print("2. MySQL credentials are correct")
        print("3. User has CREATE DATABASE privileges")
        raise

def setup_tables():
    """Create tables using SQLAlchemy"""
    try:
        from main import init_database
        init_database()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise

if __name__ == "__main__":
    print("Setting up Oratio MySQL database...")
    print("=" * 40)
    
    # Create database
    create_database()
    
    # Create tables
    setup_tables()
    
    print("=" * 40)
    print("✅ Database setup complete!")
    print(f"Database: {MYSQL_DATABASE}")
    print(f"Host: {MYSQL_HOST}:{MYSQL_PORT}")
    print(f"User: {MYSQL_USER}")
