"""
config.py
─────────
All application configuration in one place.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///campusfind.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_PERMANENT = False

    # Domain restriction for registration / login
    ALLOWED_DOMAIN = '@students.ku.ac.ke'

    # Africa's Talking
    AT_USERNAME = os.environ.get('AT_USERNAME', 'sandbox')
    AT_API_KEY  = os.environ.get('AT_API_KEY', '')
