import os

class Config:
    # SECURITY
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # MongoDB
    MONGO_URI = os.environ.get('MONGO_URI')

    # Flask-Mail (podaci se čitaju iz .env)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ('true', '1', 'yes')
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() in ('true', '1', 'yes')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')     # tvoj Gmail
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')     # Google App Password
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', MAIL_USERNAME)

    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

    USER_USERNAME = os.environ.get('USER_USERNAME')
    USER_EMAIL = os.environ.get('USER_EMAIL')
    USER_PASSWORD = os.environ.get('USER_PASSWORD')
