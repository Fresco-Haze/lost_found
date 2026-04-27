"""
routes/items.py
───────────────
Blueprint for item-related routes:
  GET        /                  – browse / home (index)
  GET        /items             – alias (same view)
  GET/POST   /report_lost
  GET/POST   /report_found
  GET        /item/<id>         – item detail
  POST       /item/<id>/claim
  GET        /my-items
  POST       /item/<id>/delete
  GET/POST   /profile
  GET        /matches
  POST       /matches/<id>/status
"""

import os
import uuid

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash
)
from functools import wraps
from werkzeug.utils import secure_filename

items_bp = Blueprint('items', __name__)


# ─── Auth decorators ──────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        if not session.get('is_admin'):
            flash('Admin access required.', 'error')
            return redirect(url_for('items.index'))
        return f(*args, **kwargs)
    return decorated


# ─── Helpers ──────────────────────────────────────────────────────────────────

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}

def _save_image(file) -> str | None:
    """Save an uploaded image file and return the filename, or None."""
    if not file or not file.filename:
        return None
    ext = os.path.splitext(secure_filename(file.filename))[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return None
    filename = f"{uuid.uuid4().hex}{ext}"
    os.makedirs('static/uploads', exist_ok=True)
    file.save(os.path.join('static/uploads', filename))
    return filename


# ─── Browse / index ───────────────────────────────────────────────────────────

@items_bp.route('/')
@login_required
def index():
    from models import Item
    status   = request.args.get('status')
    category = request.args.get('category')
    q        = request.args.get('q', '').strip()
    page     = int(request.args.get('page', 1))
    items    = Item.get_all(status=status, category=category, search=q, page=page)
    return render_template('index.html', items=items, status=status,
                           category=category, q=q, page=page)


@items_bp.route('/items')
@login_required
def items():
    """Alias for index — keeps old bookmarks alive."""
    return redirect(url_for('items.index'))


# ─── Report lost ──────────────────────────────────────────────────────────────

@items_bp.route('/report_lost', methods=['GET', 'POST'])
@login_required
def report_lost():
    if request.method == 'POST':
        from models import Item, Match

        image_filename = _save_image(request.files.get('image'))

        Item.create(
            title       = request.form.get('title', '').strip(),
            description = request.form.get('description', '').strip(),
            category    = request.form.get('category', '').strip(),
            status      = request.form.get('status', 'lost'),
            location    = request.form.get('location', '').strip(),
            date_lost   = request.form.get('date_lost', '').strip(),
            image       = image_filename,
            user_id     = session['user_id'],
        )
        Match.auto_match()
        flash('Item reported successfully!', 'success')
        return redirect(url_for('items.index'))

    return render_template('report_lost.html')


# ─── Report found ─────────────────────────────────────────────────────────────

@items_bp.route('/report_found', methods=['GET', 'POST'])
@login_required
def report_found():
    if request.method == 'POST':
        from models import Item, Match

        image_filename = _save_image(request.files.get('image'))

        Item.create(
            title       = request.form.get('title', '').strip(),
            description = request.form.get('description', '').strip(),
            category    = request.form.get('category', '').strip(),
            status      = request.form.get('status', 'found'),
            location    = request.form.get('location', '').strip(),
            date_lost   = request.form.get('date_lost', '').strip(),
            image       = image_filename,
            user_id     = session['user_id'],
        )
        Match.auto_match()
        flash('Found item reported successfully!', 'success')
        return redirect(url_for('items.index'))

    return render_template('report_found.html')


# ─── Item detail & actions ────────────────────────────────────────────────────

@items_bp.route('/item/<int:item_id>')
@login_required
def item_detail(item_id):
    from models import Item
    item = Item.get_by_id(item_id)
    if not item:
        flash('Item not found.', 'error')
        return redirect(url_for('items.index'))
    return render_template('item_detail.html', item=item)


@items_bp.route('/item/<int:item_id>/claim', methods=['POST'])
@login_required
def claim_item(item_id):
    from models import Item
    item = Item.get_by_id(item_id)
    if not item:
        flash('Item not found.', 'error')
        return redirect(url_for('items.index'))
    Item.update_status(item_id, 'claimed')
    flash('Item marked as claimed.', 'success')
    return redirect(url_for('items.item_detail', item_id=item_id))


@items_bp.route('/my-items')
@login_required
def my_items():
    from models import Item
    user_items = Item.get_by_user(session['user_id'])
    return render_template('my_items.html', items=user_items)


@items_bp.route('/item/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_item(item_id):
    from models import Item
    item = Item.get_by_id(item_id)
    if not item:
        flash('Item not found.', 'error')
        return redirect(url_for('items.my_items'))
    if item.user_id != session['user_id']:
        flash('You can only delete your own items.', 'error')
        return redirect(url_for('items.my_items'))
    Item.delete(item_id)
    flash('Item deleted.', 'success')
    return redirect(url_for('items.my_items'))


# ─── Profile ──────────────────────────────────────────────────────────────────

@items_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    from models import User
    from extensions import db
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.first_name = request.form.get('first_name', user.first_name)
        user.last_name  = request.form.get('last_name', user.last_name)
        user.phone      = request.form.get('phone', user.phone)
        db.session.commit()
        session['name'] = user.first_name
        flash('Profile updated.', 'success')
        return redirect(url_for('items.profile'))
    return render_template('profile.html', user=user)


# ─── Matches ──────────────────────────────────────────────────────────────────

@items_bp.route('/matches')
@login_required
def matches():
    from models import Match
    Match.auto_match()
    all_matches = Match.get_all()
    return render_template('matches.html', matches=all_matches)


@items_bp.route('/matches/<int:match_id>/status', methods=['POST'])
@admin_required
def update_match_status(match_id):
    from models import Match
    status = request.form.get('status')
    if status in ('approved', 'rejected'):
        Match.update_status(match_id, status)
        flash(f'Match {status}.', 'success')
    return redirect(url_for('items.matches'))
