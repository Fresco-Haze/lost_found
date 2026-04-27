from app import app
from models import db, User, Item
from werkzeug.security import generate_password_hash

with app.app_context():
    # Only insert if no test user exists
    user = User.query.filter_by(email='test@students.ku.ac.ke').first()
    if not user:
        user = User(
            first_name='Test',
            last_name='User',
            email='test@students.ku.ac.ke',
            student_id='A1234567',
            phone='0712345678',
            role='student',
            password_hash=generate_password_hash('password123'),
        )
        user.is_verified = True
        db.session.add(user)
        db.session.commit()
    elif not user.is_verified:
        user.is_verified = True
        db.session.commit()
    
    # Insert some items if empty
    if Item.query.count() == 0:
        item1 = Item(
            title='Blue Backpack',
            description='Lost near the library. Brand is Nike. Contains notebooks.',
            category='bags',
            status='lost',
            location='Main Library',
            date_lost='2026-04-01',
            user_id=user.id
        )
        item2 = Item(
            title='Macbook Pro Charger',
            description='Found a white apple charger in RM 101 left on a desk.',
            category='electronics',
            status='found',
            location='Science Building Rm 101',
            date_lost='2026-04-02',
            user_id=user.id
        )
        db.session.add(item1)
        db.session.add(item2)
        db.session.commit()

print("Database seeded with test user and items.")
