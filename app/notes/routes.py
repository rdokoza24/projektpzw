from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import notes_bp
from ..extensions import mongo
from ..models import User 
from ..utils import role_required, sanitize_html
from bson.objectid import ObjectId
from datetime import datetime


@notes_bp.route('/')
@login_required
def list_notes():
    # Funkcionalnost za korisnika: prikazuje samo njegove bilješke
    notes = list(mongo.db.notes.find({'user_id': ObjectId(current_user.id)}).sort('created_at', -1))
    return render_template('notes/list.html', notes=notes)

@notes_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_note(): # <-- OVO JE ENDPOINT notes.create_note
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()

        # sanitizacija
        sanitized_title = sanitize_html(title)
        sanitized_content = sanitize_html(content)
        

        if not sanitized_title:
            flash('Naslov je obavezan.', 'warning')
            return render_template('notes/create.html')
            
        note = {
            'user_id': ObjectId(current_user.id),
            'title': sanitized_title, # Koristimo sanitizirani
            'content': sanitized_content, # Koristimo sanitizirani
            'created_at': datetime.utcnow()
        }
        mongo.db.notes.insert_one(note)
        flash('Bilješka spremljena.', 'success')
        return redirect(url_for('notes.list_notes'))
    return render_template('notes/create.html')

@notes_bp.route('/edit/<note_id>', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    # Funkcionalnost za korisnika: uređivanje samo vlastite bilješke
    try:
        note = mongo.db.notes.find_one({'_id': ObjectId(note_id)})
    except:
        flash('Bilješka nije pronađena.', 'danger')
        return redirect(url_for('notes.list_notes'))

    if not note or note.get('user_id') != ObjectId(current_user.id):
        flash('Nije pronađena bilješka ili nemate dozvolu za uređivanje.', 'danger')
        return redirect(url_for('notes.list_notes'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()

        # sanitizacija
        sanitized_title = sanitize_html(title)
        sanitized_content = sanitize_html(content)


        if not sanitized_title:
            flash('Naslov je obavezan.', 'warning')
            # Proslijeđivanje note da bi se forma ponovno popunila
            note['title'] = title
            note['content'] = content 
            return render_template('notes/edit.html', note=note, admin_mode=False)

        mongo.db.notes.update_one(
            {'_id': ObjectId(note_id)},
            {'$set': {
                'title': sanitized_title, # Koristimo sanitizirani
                'content': sanitized_content, # Koristimo sanitizirani
                'updated_at': datetime.utcnow()
            }}
        )
        flash('Bilješka uspješno ažurirana.', 'success')
        return redirect(url_for('notes.list_notes'))

    return render_template('notes/edit.html', note=note, admin_mode=False) # admin_mode=False za korisnika

@notes_bp.route('/delete/<note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    # Funkcionalnost za korisnika: brisanje samo vlastite bilješke
    try:
        result = mongo.db.notes.delete_one({
            '_id': ObjectId(note_id),
            'user_id': ObjectId(current_user.id)
        })
    except:
        flash('Bilješka nije pronađena.', 'danger')
        return redirect(url_for('notes.list_notes'))

    if result.deleted_count == 1:
        flash('Bilješka uspješno obrisana.', 'success')
    else:
        flash('Nije pronađena bilješka ili nemate dozvolu za brisanje.', 'danger')

    return redirect(url_for('notes.list_notes'))



#RUTE ZA ADMIN DASHBOARD

@notes_bp.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    #(kod za dohvaćanje bilješki)
    #(kod za spajanje bilješki s korisničkim imenom)
    all_notes_docs = list(mongo.db.notes.find().sort('created_at', -1))
    user_ids = [n.get('user_id') for n in all_notes_docs if n.get('user_id')]
    unique_user_ids = list(set(user_ids))
    users_data = list(mongo.db.users.find({'_id': {'$in': unique_user_ids}}, {'username': 1}))
    user_map = {u['_id']: u['username'] for u in users_data}
    notes_with_users = []
    for note in all_notes_docs:
        note['username'] = user_map.get(note.get('user_id'), 'Nepoznat')
        notes_with_users.append(note)

    return render_template('admin/admin_dashboard.html', notes=notes_with_users) 


@notes_bp.route('/admin/edit/<note_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin') 
def admin_edit_note(note_id):
    try:
        note = mongo.db.notes.find_one({'_id': ObjectId(note_id)})
    except:
        flash('Bilješka nije pronađena.', 'danger')
        return redirect(url_for('notes.admin_dashboard'))

    if not note:
        flash('Bilješka nije pronađena.', 'danger')
        return redirect(url_for('notes.admin_dashboard'))

    # Dohvati korisničko ime za prikaz
    user = User.get_by_id(note.get('user_id'))
    note['username'] = user.username if user else 'Nepoznat'

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        
        #sanitizacija
        sanitized_title = sanitize_html(title)
        sanitized_content = sanitize_html(content)


        if not sanitized_title:
            flash('Naslov je obavezan.', 'warning')
            # Proslijeđivanje note da bi se forma ponovno popunila
            note['title'] = title
            note['content'] = content 
            return render_template('notes/edit.html', note=note, admin_mode=True)

        mongo.db.notes.update_one(
            {'_id': ObjectId(note_id)},
            {'$set': {
                'title': sanitized_title, # Koristimo sanitizirani
                'content': sanitized_content, # Koristimo sanitizirani
                'updated_at': datetime.utcnow()
            }}
        )
        flash(f'Bilješka "{title}" (od korisnika: {note["username"]}) uspješno ažurirana (Admin).', 'success')
        return redirect(url_for('notes.admin_dashboard'))

    return render_template('notes/edit.html', note=note, admin_mode=True)


@notes_bp.route('/admin/delete/<note_id>', methods=['POST'])
@login_required
@role_required('admin')
def admin_delete_note(note_id):
    try:
        result = mongo.db.notes.delete_one({'_id': ObjectId(note_id)})
    except Exception as e:
        flash(f'Greška prilikom brisanja bilješke: {e}', 'danger')
        return redirect(url_for('notes.admin_dashboard'))

    if result.deleted_count == 1:
        flash(f'Bilješka ID: {note_id} uspješno obrisana (Admin).', 'success')
    else:
        flash('Bilješka nije pronađena.', 'danger')

    return redirect(url_for('notes.admin_dashboard'))