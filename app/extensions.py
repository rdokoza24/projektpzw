from flask_pymongo import PyMongo
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_principal import Principal

mongo = PyMongo()
login_manager = LoginManager()
bootstrap = Bootstrap5()
mail = Mail()
principal=Principal()
limiter = Limiter(key_func=get_remote_address)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per minute"]  # <-- globalna ograničenja
)