from flask import Blueprint

notes_bp = Blueprint('notes', __name__, template_folder='templates', url_prefix='/notes')

from . import routes
