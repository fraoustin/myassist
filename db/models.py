from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
from db import db


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, index=True, unique=True)
    name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    lastconnection = db.Column(db.Date, nullable=True)
    isadmin = db.Column(db.Boolean, default=False, nullable=False)
    gravatar = db.Column(db.Boolean, default=False, nullable=False)
    apikey = db.Column(db.String, nullable=True)
    token = db.Column(db.String, nullable=True)
    group = db.Column(db.String, nullable=True)

    def __setattr__(self, name, value):
        if name in ('isadmin', 'gravatar') and type(value) == str:
            if value in ['true', 'True']:
                value = True
            else:
                value = False
        if name == 'password':
            value = generate_password_hash(value)
        db.Model.__setattr__(self, name, value)

    def __getattribute__(self, name):
        if name in ('lastconnection'):
            if db.Model.__getattribute__(self, name) is not None:
                return db.Model.__getattribute__(self, name).strftime('%d/%m/%Y')
            else:
                return ""
        if name == 'urlgravatar':
            return "https://www.gravatar.com/avatar/" + hashlib.md5(self.email.encode().lower()).hexdigest()
        if name == "flows":
            return []
        if name not in ('id') and db.Model.__getattribute__(self, name) is None:
            return ""
        return db.Model.__getattribute__(self, name)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the id to satisfy Flask-Login's requirements."""
        return self.id

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

    def is_authenticated(self):
        return True

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def has_authorization(self, modul, key):
        if self.isadmin is True:
            return True
        authorizations = Authorization.get(self.group)
        for authorization in authorizations:
            if authorization.modul == modul and authorization.key == key:
                return True
        return False


class GroupOfAuthorization(db.Model):
    __tablename__ = 'groupofauthorization'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)

    def clean_authorization(self):
        for auth in Authorization.query.filter_by(idgroup=self.id).all():
            auth.remove()

    def add_authorisation(self, modul, key):
        auth = Authorization()
        auth.idgroup = self.id
        auth.modul = modul
        auth.key = key
        auth.save()

    @property
    def authorizations(self):
        return Authorization.query.filter_by(idgroup=self.id).all()


class Authorization(db.Model):
    __tablename__ = 'authorization'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idgroup = db.Column(db.Integer, nullable=False)
    modul = db.Column(db.String, nullable=False)
    key = db.Column(db.String, nullable=False)

    @classmethod
    def get(cls, idgroup):
        try:
            return cls.query.filter_by(idgroup=idgroup).all()
        except Exception:
            return None


class Param(db.Model):
    __tablename__ = 'param'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String, nullable=False)
    module = db.Column(db.String, nullable=False)
    value = db.Column(db.String, nullable=True)

    @classmethod
    def get(cls, module, key):
        try:
            return cls.query.filter_by(key=key).first()
        except Exception:
            return None

    @classmethod
    def getValue(cls, module, key, default=""):
        try:
            return cls.query.filter_by(key=key).first().value
        except Exception:
            return None


class ParamRegister(Param):
    __tablename__ = 'param'

    @classmethod
    def get(cls, key):
        return Param.get('register', key)

    @classmethod
    def getValue(cls, key, default=""):
        return Param.getValue('register', key, default)

    def __setattr__(self, name, value):
        db.Model.__setattr__(self, name, value)
        db.Model.__setattr__(self, 'module', 'register')


class ParamApp(Param):
    __tablename__ = 'param'

    @classmethod
    def get(cls, key):
        return Param.get('app', key)

    @classmethod
    def getValue(cls, key, default=""):
        return Param.getValue('app', key, default)

    def __setattr__(self, name, value):
        db.Model.__setattr__(self, name, value)
        db.Model.__setattr__(self, 'module', 'app')
