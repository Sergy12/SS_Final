from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note, AuditLog, User, create_admin
from . import db, action
import json

views = Blueprint('views', __name__)

@views.route('/admin/users', methods=['GET'])
@login_required
def admin_users(): # Ruta para mostrar usuarios (solo para administradores)
    if current_user.is_admin:  # Verifica si el usuario es administrador
        page = request.args.get('page', 1, type=int)
        per_page = 5
        users = User.query.paginate(page=page, per_page=per_page)  # Obtiene todos los usuarios
        return render_template("admin_users.html", users=users, current_user=current_user, user=current_user)  # Renderiza una plantilla para mostrar usuarios
    else:
        flash('Access denied. Only administrators can view users.', category='error')
        return redirect(url_for('views.home'))
    
@views.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required
def admin_delete_user(user_id): # Ruta para eliminar usuarios (solo para administradores)
    if current_user.is_admin:  # Verifica si el usuario es administrador
        user = User.query.get(user_id)  # Obtiene el usuario por su ID
        if user:
            db.session.delete(user)
            db.session.commit()
            log_admin_event(current_user.id, f"User {user.email} deleted by admin")
            flash('User deleted successfully.', category='success')
        else:
            flash('User not found.', category='error')
    else:
        flash('Access denied. Only administrators can delete users.', category='error')
    return redirect(url_for('views.admin_users'))

def log_admin_event(user_id, action): # Función para registrar eventos en AuditLog
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
            current_user.notes.append(new_note) 
            log_admin_event(current_user.id, action[5]) # Registro de evento - Agregar nota por un admin
            flash('Note added!', category='success')
    page = request.args.get('page', 1, type=int)
    per_page = 5
    user_notes = Note.query.filter_by(user_id=current_user.id).paginate(page=page, per_page=per_page)
    return render_template("home.html", user=current_user, user_notes=user_notes)

@views.route('/delete-note/<int:note_id>', methods=['GET'])
@login_required
def delete_note(note_id):
    note = Note.query.get(note_id)
    if not note:
        flash('Note not found!', category='error')
        return redirect(url_for('views.home'))
    
    if note.user_id != current_user.id:
        flash('Access denied. You are not authorized to delete this note.', category='error')
        return redirect(url_for('views.home'))
    
    db.session.delete(note)
    db.session.commit()
    flash('Note deleted successfully!', category='success')
    return redirect(url_for('views.home'))


@views.route('/edit-note/<int:note_id>', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    note = Note.query.get(note_id)
    if not note:
        flash('Note not found!', category='error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        new_data = request.form.get('new_data')
        if len(new_data) < 1:
            flash('Note is too short!', category='error')
        else:
            note.data = new_data
            db.session.commit()
            flash('Note updated!', category='success')
            return redirect(url_for('views.home'))

    return render_template("edit_note.html", note=note, user=current_user)

@views.route('/profile/<int:user_id>', methods=['GET'])
@login_required
def user_profile(user_id):
    profile_user = User.query.get(user_id)
    if not profile_user:
        flash('User not found!', category='error')
        return redirect(url_for('views.home'))

    # Si el usuario actual NO es administrador y no es el mismo que el perfil seleccionado
    if not current_user.is_admin and current_user.id != profile_user.id:
        flash('Access denied. You are not authorized to view this profile.', category='error')
        return redirect(url_for('views.home'))

    # Si el usuario actual NO es administrador pero es el mismo que el perfil seleccionado
    if not current_user.is_admin and current_user.id == profile_user.id:
        return render_template("profile.html", user=current_user, profile_user=profile_user)

    # Si el usuario actual es administrador, muestra el perfil del usuario seleccionado
    return render_template("profile.html", user=current_user, profile_user=profile_user)





@views.route('/add-note/<int:user_id>', methods=['POST'])
@login_required
def add_note(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('User not found!', category='error')
        return redirect(url_for('views.home'))

    if current_user.is_admin or current_user.id == user.id:
        note_text = request.form.get('note')
        if not note_text:
            flash('Note cannot be empty!', category='error')
        else:
            admin_name = None
            if current_user.is_admin:
                admin_name = current_user.first_name  # Usamos 'first_name' como nombre del admin

            new_note = Note(data=note_text, user_id=user_id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added successfully!', category='success')
    else:
        flash('Access denied. You are not authorized to add notes for this user.', category='error')

    return redirect(url_for('views.user_profile', user_id=user_id))
