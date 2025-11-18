from functools import wraps
from flask import abort
from flask_principal import Permission, RoleNeed, identity_loaded, current_app
from flask_login import current_user
import bleach 

# Definirajte dozvoljene tagove i atribute za sanitizaciju
ALLOWED_TAGS = [
    'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'p', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'hr', 'br', 'span'
]
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'abbr': ['title'],
    'acronym': ['title'],
    # Dodajte 'class' ako želite da stilovi iz Markdowna rade (npr. klase za tablice)
}

def sanitize_html(html_content):
    """
    Sanitizira HTML sadržaj koristeći bleach, ograničavajući ga na sigurne tagove.
    """
    if not html_content:
        return ""
        
    return bleach.clean(
        html_content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True # Uklanja nedozvoljene tagove zajedno s njihovim sadržajem
    )

def role_required(role):
    """
    Dekorator koji provjerava ima li prijavljeni korisnik ulogu.
    Ako nije autoriziran -> abort(403).
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Ako nema korisnika, abort
            if not current_user or not current_user.is_authenticated:
                abort(403)
            # Ako korisnik nema rolu, abort
            if not hasattr(current_user, 'has_role') or not current_user.has_role(role):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator