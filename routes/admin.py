"""
routes/admin.py
───────────────
Blueprint for admin-only routes:
  GET        /admin
  POST       /admin/item/<id>/delete
  POST       /admin/item/<id>/status
  GET/POST   /admin/item/<id>/edit
  POST       /admin/user/<id>/promote
  POST       /admin/user/<id>/delete
"""

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash
)
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ─── Auth decorator ───────────────────────────────────────────────────────────

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


# ─── Dashboard ────────────────────────────────────────────────────────────────

@admin_bp.route('/')
@admin_required
def dashboard():
    from models import Item, User, Match
    stats = {
        'total_items':    Item.count_all(),
        'lost':           Item.count_by_status('lost'),
        'found':          Item.count_by_status('found'),
        'claimed':        Item.count_by_status('claimed'),
        'total_users':    User.count_all(),
        'pending_matches': Match.count_pending(),
    }
    recent_items = Item.get_all(page=1)
    users        = User.query.order_by(User.id.desc()).all()
    return render_template('admin.html', stats=stats,
                           recent_items=recent_items, users=users)


# ─── Item management ──────────────────────────────────────────────────────────

@admin_bp.route('/item/<int:item_id>/delete', methods=['POST'])
@admin_required
def delete_item(item_id):
    from models import Item
    Item.delete(item_id)
    flash('Item deleted.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/item/<int:item_id>/status', methods=['POST'])
@admin_required
def update_status(item_id):
    from models import Item
    new_status = request.form.get('status')
    if new_status in ('lost', 'found', 'claimed'):
        Item.update_status(item_id, new_status)
        flash('Status updated.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/item/<int:item_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_item(item_id):
    from models import Item
    from extensions import db
    item = Item.query.get(item_id)
    if not item:
        flash('Item not found.', 'error')
        return redirect(url_for('admin.dashboard'))
    if request.method == 'POST':
        item.title       = request.form.get('title', item.title)
        item.description = request.form.get('description', item.description)
        item.category    = request.form.get('category', item.category)
        item.location    = request.form.get('location', item.location)
        item.date_lost   = request.form.get('date_lost', item.date_lost)
        db.session.commit()
        flash('Item updated.', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin_edit.html', item=item)


# ─── User management ──────────────────────────────────────────────────────────

@admin_bp.route('/user/<int:user_id>/promote', methods=['POST'])
@admin_required
def promote_user(user_id):
    from models import User
    from extensions import db
    user = User.query.get(user_id)
    if user:
        user.is_admin = True
        db.session.commit()
        flash(f'{user.first_name} promoted to admin.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    from models import User
    from extensions import db
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted.', 'success')
    return redirect(url_for('admin.dashboard'))
