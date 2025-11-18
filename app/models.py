from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from bson.objectid import ObjectId
from .extensions import mongo
from flask import current_app
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

class User(UserMixin):
    def __init__(self, data):
        # data is document from MongoDB
        self._data = data

    @property
    def id(self):
        # flask-login expects id property (string)
        return str(self._data.get('_id'))

    @property
    def username(self):
        return self._data.get('username')

    @property
    def email(self):
        return self._data.get('email')

    @property
    def password_hash(self):
        return self._data.get('password_hash')

    @property
    def email_confirmed(self):
        return bool(self._data.get('email_confirmed', False))

    @property
    def roles(self):
        # returns list of roles (strings)
        return list(self._data.get('roles', []))

    @staticmethod
    def _get_serializer():
        secret = current_app.config['SECRET_KEY']
        return URLSafeTimedSerializer(secret)

    @staticmethod
    def get_by_id(user_id):
        try:
            doc = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        except Exception:
            return None
        if doc:
            return User(doc)
        return None

    @staticmethod
    def get_by_username(username):
        doc = mongo.db.users.find_one({'username': username})
        if doc:
            return User(doc)
        return None

    @staticmethod
    def get_by_email(email):
        doc = mongo.db.users.find_one({'email': email})
        if doc:
            return User(doc)
        return None

    @staticmethod
    def create(username, email, password, roles=None):
        """
        Kreira korisnika i vraća User instancu.
        roles: list of role strings, npr ['user'] ili ['admin']
        """
        if roles is None:
            roles = []
        password_hash = generate_password_hash(password)
        user_doc = {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'email_confirmed': False,
            'roles': roles
        }
        result = mongo.db.users.insert_one(user_doc)
        user_doc['_id'] = result.inserted_id
        return User(user_doc)

    def add_role(self, role):
        """
        Dodaje rolu (string) korisniku u DB (ako već ne postoji).
        """
        if role not in self.roles:
            mongo.db.users.update_one({'_id': ObjectId(self._data['_id'])}, {'$addToSet': {'roles': role}})
            # također update lokalni objekt
            self._data.setdefault('roles', [])
            if role not in self._data['roles']:
                self._data['roles'].append(role)
            return True
        return False

    def has_role(self, role):
        return role in self.roles

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self):
        """
        Generate a time-limited token for email confirmation.
        """
        s = self._get_serializer()
        return s.dumps(self.email, salt='email-confirm-salt')

    @staticmethod
    def confirm_token(token, expiration=3600):
        """
        Return email if token valid, else None.
        expiration in seconds (default 3600 -> 1h).
        """
        s = User._get_serializer()
        try:
            email = s.loads(token, salt='email-confirm-salt', max_age=expiration)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        return email

    def mark_email_confirmed(self):
        """
        Set email_confirmed to True in DB and update local object.
        """
        mongo.db.users.update_one({'_id': ObjectId(self._data['_id'])}, {'$set': {'email_confirmed': True}})
        self._data['email_confirmed'] = True
        return True
