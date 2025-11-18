from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from . import auth_bp
from ..models import User
from ..extensions import mongo, mail
from flask_principal import Identity, AnonymousIdentity, identity_changed
# FORMS
from .forms import LoginForm, RegistrationForm
# MAIL
from flask_mail import Message

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()

    if form.validate_on_submit():
        username_or_email = form.username.data
        password = form.password.data

        user = User.get_by_username(username_or_email) or User.get_by_email(username_or_email)
        
        if user and user.check_password(password):
            if not user.email_confirmed:
                flash('Morate potvrditi email prije prijave. Provjerite svoj inbox.', 'warning')
                return redirect(url_for('auth.login'))

            login_user(user)

            # obavijestimo Flask-Principal da je identitet promijenjen
            identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))
            
            next_page = request.args.get('next')
            # sigurnosna provjera next
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('main.index')
            return redirect(next_page)
        
        flash('Neispravno korisničko ime/email ili lozinka.', 'danger')
        
    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()

    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip().lower()
        password = form.password.data

        # Kreiraj korisnika s početnom rolom 'user'
        user = User.create(username, email, password, roles=['user'])

        # Generiraj token i pošalji potvrdu
        token = user.generate_confirmation_token()
        confirm_url = url_for('auth.confirm_email', token=token, _external=True)

        # Render email template (HTML)
        html = render_template('auth/confirm_email.html', confirm_url=confirm_url, user=user)

        # Send mail
        subject = "Potvrdi svoj email"
        msg = Message(subject=subject, recipients=[user.email], html=html)
        try:
            mail.send(msg)
            flash('Registracija uspješna. Poslan je email za potvrdu. Provjeri svoj inbox.', 'success')
        except Exception as e:
            # Ako slanje maila ne uspije — izbaci grešku, ali korisnik je kreiran
            current_app.logger.exception("Neuspjelo slanje potvrde emaila: %s", e)
            flash('Registracija uspješna, ali slanje emaila nije uspjelo. Kontaktiraj administratora.', 'warning')

        # Ne logiramo odmah korisnika — tražimo potvrdu emaila
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/confirm/<token>')
def confirm_email(token):
    email = User.confirm_token(token)
    if not email:
        flash('Link za potvrdu je neispravan ili je istekao.', 'danger')
        return redirect(url_for('auth.login'))

    user = User.get_by_email(email)
    if not user:
        flash('Korisnik nije pronađen.', 'danger')
        return redirect(url_for('auth.register'))

    if user.email_confirmed:
        flash('Email je već potvrđen. Možeš se prijaviti.', 'info')
        return redirect(url_for('auth.login'))

    user.mark_email_confirmed()
    flash('Email je uspješno potvrđen. Sada se možete prijaviti.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()

    # obavijestimo Flask-Principal da je korisnik anonimni sada
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())

    flash('Uspješno ste se odjavili.', 'info')
    return redirect(url_for('auth.login'))
