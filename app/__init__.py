from flask import Flask, render_template
from .extensions import mongo, login_manager, bootstrap, mail, principal, limiter
from .auth import auth_bp
from .main import main_bp
from .notes import notes_bp
import markdown

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # init extensions
    mongo.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    principal.init_app(app)

    # register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(notes_bp)
    
    register_error_handlers(app)
   
    # login settings
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    #Custom Jinja filter za Markdown konverziju
    @app.template_filter('markdown_to_html')
    def markdown_to_html_filter(text):
        if not text:
            return ""
        # Koristimo 'fenced_code' ekstenziju za podršku blokova koda
        return markdown.markdown(str(text), extensions=['fenced_code'])

    # import here to avoid circular imports
    from .models import User
    from .extensions import mongo as _mongo

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)

    # Automatsko kreiranje admin korisnika (ako ne postoji)
    with app.app_context():
        _create_default_admin()
        _create_default_user()

    return app

def _create_default_admin():
    """
    Stvara default admin account čiji se podaci čitaju iz ENV varijabli.
    Ako admin već postoji, ništa se ne radi.
    """
    from flask import current_app
    from .models import User
    from .extensions import mongo
    from bson.objectid import ObjectId

    admin_username = current_app.config['ADMIN_USERNAME']
    admin_email = current_app.config['ADMIN_EMAIL']
    admin_password = current_app.config['ADMIN_PASSWORD']

    # Provjeri postoji li admin
    existing = mongo.db.users.find_one({'username': admin_username})
    if existing:
        return False

    # Kreiraj admin korisnika s rolom 'admin'
    admin_user = User.create(admin_username, admin_email, admin_password, roles=['admin'])

    # Označi email potvrđenim
    mongo.db.users.update_one(
        {'_id': ObjectId(admin_user._data['_id'])},
        {'$set': {'email_confirmed': True}}
    )

    return True

def _create_default_user():
    """
    Stvara default korisnika 'user' sa šifrom 'user123'.
    Ako korisnik već postoji, ništa se ne radi.
    """
    from flask import current_app
    from .models import User
    from .extensions import mongo
    from bson.objectid import ObjectId

    username = current_app.config['USER_USERNAME']
    email = current_app.config['USER_EMAIL']
    password = current_app.config['USER_PASSWORD']

    # Provjeri postoji li korisnik
    existing = mongo.db.users.find_one({'username': username})
    if existing:
        return False

    # Kreiraj korisnika s rolom 'user'
    user = User.create(username, email, password, roles=['user'])

    # Označi email potvrđenim
    mongo.db.users.update_one(
        {'_id': ObjectId(user._data['_id'])},
        {'$set': {'email_confirmed': True}}
    )

    return True

def register_error_handlers(app):
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return render_template("errors/429.html"), 429

    @app.errorhandler(500)
    def internal_error(e):
        return render_template("errors/500.html"), 500
