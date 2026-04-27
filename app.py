"""
app.py
──────
Application factory.  All routes live in routes/auth.py,
routes/items.py, and routes/admin.py.

Run:
    python app.py           (development)
    flask run               (via FLASK_APP=app)
"""

import os
from flask import Flask
from config import Config
from extensions import db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialise extensions
    db.init_app(app)

    # Create DB tables on first run
    with app.app_context():
        db.create_all()
        os.makedirs('static/uploads', exist_ok=True)

    # Register blueprints
    from routes.auth  import auth_bp
    from routes.items import items_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(items_bp)
    app.register_blueprint(admin_bp)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)