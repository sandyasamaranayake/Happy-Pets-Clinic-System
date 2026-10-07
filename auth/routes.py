# ==============================================================================
# Module: User Authentication & Security
# Developer: R.M.S.M. Samaranayake (Leader)
# JIRA Tasks: SCRUM-6 (Login UI), SCRUM-7 (Password Reset)
# ==============================================================================

import random
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

# Blueprint setup for authentication module
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Mock store for OTP codes
otp_store = {}

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('email', '').strip()  # Form field name or email
        password = request.form.get('password', '').strip()
        selected_role = request.form.get('role', '').strip()

        # Search user by username
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            if selected_role and user.role and user.role.lower() != selected_role.lower():
                flash(f'Role mismatch! Registered as {user.role}', 'danger')
                return render_template('auth/login.html')

            login_user(user)
            flash('Successfully logged in!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        phone = request.form.get('phone')
        address = request.form.get('address')
        password = request.form.get('password')
        role = request.form.get('role')

        # Check existing username
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already taken. Please choose another.', 'warning')
            return redirect(url_for('auth.register'))

        # Create new user
        hashed_pw = generate_password_hash(password)
        new_user = User(
            name=name,
            username=username,
            phone=phone,
            address=address,
            password=hashed_pw,
            role=role
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        action = request.form.get('action')

        if action == 'send_link':
            flash(f'Password reset link has been sent to {email}', 'success')
            return redirect(url_for('auth.forgot_password'))

        elif action == 'send_otp':
            otp = random.randint(100000, 999999)
            otp_store[email] = otp
            print(f"Generated OTP for {email}: {otp}")
            
            flash(f'OTP sent to {email}. (Check terminal for test OTP)', 'info')
            return redirect(url_for('auth.verify_otp', email=email))

    return render_template('auth/forgot_password.html')


@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    email = request.args.get('email')
    
    if request.method == 'POST':
        user_otp = request.form.get('otp')
        stored_otp = otp_store.get(email)

        if stored_otp and str(stored_otp) == user_otp:
           
            user = User.query.filter_by(email=email).first()
            if user:
                user.password = generate_password_hash('1234')
                db.session.commit()

            otp_store.pop(email, None)
            flash('OTP verified successfully! Password reset to 1234. Please login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid OTP code. Please try again.', 'danger')

    return render_template('auth/verify_otp.html', email=email)


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    email = request.args.get('email')
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if new_password == confirm_password:
            if email:
                user = User.query.filter_by(email=email).first()
                if user:
                    user.password = generate_password_hash(new_password)
                    db.session.commit()

                    flash('Password reset successful! You can now login.', 'success')
                    return redirect(url_for('auth.login'))
                else:
                    flash('User account not found.', 'danger')
        else:
            flash('Passwords do not match.', 'danger')

    return render_template('auth/reset_password.html')