from flask import Blueprint
from ..models import User
from ..extensions import login_manager

auth_bp = Blueprint('auth', __name__, template_folder='templates', url_prefix='/auth')

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

from . import routes
