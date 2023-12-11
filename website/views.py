from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note, AuditLog, User
from . import db, action
import json

views = Blueprint('views', __name__)

@views.route('/admin/users', methods=['GET'])
@login_required
def admin_users():
    if current_user.is_admin:  # Verifica si el usuario es administrador
        users = User.query.all()  # Obtiene todos los usuarios
        return render_template("admin_users.html", users=users, current_user=current_user)  # Renderiza una plantilla para mostrar usuarios
    else:
        flash('Access denied. Only administrators can view users.', category='error')
        return redirect(url_for('views.home'))
    
@views.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    if current_user.is_admin:  # Verifica si el usuario es administrador
        user = User.query.get(user_id)  # Obtiene el usuario por su ID
        if user:
            db.session.delete(user)
            db.session.commit()
            flash('User deleted successfully.', category='success')
        else:
            flash('User not found.', category='error')
    else:
        flash('Access denied. Only administrators can delete users.', category='error')
    return redirect(url_for('views.admin_users'))

def log_event(user_id, action):
    entry = AuditLog(user_id=user_id, action=action)
    db.session.add(entry)
    db.session.commit()

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            log_event(current_user.id, action[5])
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)

@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
            log_event(current_user.id, action[6])

    return jsonify({})