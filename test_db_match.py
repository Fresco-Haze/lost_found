from app import create_app
from extensions import db
from models import User, Item, Match

app = create_app()

with app.app_context():
    # 1. Ensure we have a dummy user
    user = User.query.filter_by(email='test_ai@example.com').first()
    if not user:
        user = User.create(
            first_name='AI',
            last_name='Tester',
            email='test_ai@example.com',
            student_id='AI001',
            phone='0700000000',
            role='student',
            password_hash='dummy'
        )

    # 2. Create a lost item
    lost_item = Item.create(
        title='MacBook Pro 14-inch',
        description='Silver laptop with a sticker of a cat on the back. It has a tiny dent on the right corner.',
        category='Electronics',
        status='lost',
        location='Cafeteria near the window',
        date_lost='2024-05-10',
        image=None,
        user_id=user.id
    )
    print(f"Reported LOST item: {lost_item.title} (ID: {lost_item.id})")

    # 3. Create a found item (similar description, different wording)
    found_item = Item.create(
        title='Apple Laptop',
        description='Found a silver Macbook. There is a kitty sticker on the lid and a small scratch or dent on the side.',
        category='Electronics',
        status='found',
        location='Main Cafeteria tables',
        date_lost='2024-05-10',
        image=None,
        user_id=user.id
    )
    print(f"Reported FOUND item: {found_item.title} (ID: {found_item.id})")

    # 4. Trigger auto match
    print("Running auto_match()...")
    new_matches = Match.auto_match()
    print(f"New matches found: {new_matches}")

    # 5. Check if our items were matched
    match = Match.query.filter_by(lost_item_id=lost_item.id, found_item_id=found_item.id).first()
    if match:
        print("SUCCESS! The items were successfully matched by AI.")
    else:
        print("FAILURE! The items were not matched.")
