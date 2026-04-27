"""
routes/auth.py
──────────────
Blueprint for authentication routes:
  GET/POST  /login
  GET/POST  /register
  GET       /logout
"""

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash, current_app
)
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _allowed_email(email: str) -> bool:
    domain = current_app.config['ALLOWED_DOMAIN']
    return email.endswith(domain)


# ─── Routes ───────────────────────────────────────────────────────────────────

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('items.index'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not _allowed_email(email):
            flash('Only @students.ku.ac.ke email addresses are allowed.', 'error')
            return render_template('login.html')

        from models import User
        user = User.get_by_email(email)

        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid email or password.', 'error')
            return render_template('login.html')

        if not user.is_verified:
            flash('Please verify your email before logging in.', 'error')
            return render_template('login.html')

        session['user_id'] = user.id
        session['name']    = user.first_name
        session['email']   = user.email
        session['is_admin'] = user.is_admin
        return redirect(url_for('items.index'))

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('items.index'))

    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name  = request.form.get('last_name', '').strip()
        email      = request.form.get('email', '').strip().lower()
        student_id = request.form.get('student_id', '').strip()
        phone      = request.form.get('phone', '').strip()
        role       = request.form.get('role', 'student')
        password   = request.form.get('password', '')
        confirm_pw = request.form.get('confirm_password', '')

        if not _allowed_email(email):
            flash('Only @students.ku.ac.ke email addresses are allowed.', 'error')
            return render_template('register.html')

        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'error')
            return render_template('register.html')

        if password != confirm_pw:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')

        from models import User
        if User.get_by_email(email):
            flash('An account with that email already exists.', 'error')
            return render_template('register.html')

        password_hash = generate_password_hash(password)
        User.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            student_id=student_id,
            phone=phone,
            role=role,
            password_hash=password_hash
        )

        flash('Account created! You can now sign in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
