from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, AuditLog
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, action
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)

def log_event(user_id, action):
    entry = AuditLog(user_id=user_id, action=action)
    db.session.add(entry)
    db.session.commit()


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password1 = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password1):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                log_event(user.id, action[0])
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
                log_event(user.id, action[1])
        else:
            flash('Email does not exist.', category='error')
            log_event(None, action[1])

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    log_event(current_user.id, action[4])
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        is_admin = request.form.get('isAdmin')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
            log_event(None, action[3])
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
            log_event(None, action[3])
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
            log_event(None, action[3])
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
            log_event(None, action[3])
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
            log_event(None, action[3])
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='pbkdf2', salt_length=16), is_admin=False)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            user = User.query.filter_by(email=email).first()
            log_event(user.id, action[2])
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)