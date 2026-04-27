"""
extensions.py
─────────────
Shared Flask extensions — imported by models and routes to avoid
circular import issues.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
