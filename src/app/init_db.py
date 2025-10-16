#!/usr/bin/env python3
"""
Initialize the database with all tables.

This script creates all the database tables needed for the school management system.
Run this file to set up a fresh database with empty tables.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import app, db

with app.app_context():
    """
    Create all database tables defined in the models.
    
    This will create whatever tables are defined in models.py.
    The database file is created in the instance folder.
    """
    db.create_all()
    print("Database created successfully!")
    print(f"Database file location: {app.config['SQLALCHEMY_DATABASE_URI']}")