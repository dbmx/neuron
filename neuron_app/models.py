from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from slugify import slugify
from datetime import datetime
from sqlalchemy import Column, Integer, Date, DateTime, String


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    comments = db.relationship('Comment', backref='author', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    # Dodatne kolone po potrebi

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    slug = db.Column(db.String(255), unique=True)
    featured_image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    click_count = db.Column(db.Integer, default=0)
    comments = db.relationship('Comment', backref='news', lazy='dynamic')

    def set_slug(self, title):
        self.slug = slugify(title)[:30]

class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_header = db.Column(db.Boolean, default=False)
    # Dodatne kolone po potrebi

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'), nullable=False)

class Visit(db.Model):
    __tablename__ = 'visits'
    id = Column(Integer, primary_key=True)
    visits = Column(Integer, default=0)
    date = Column(Date, default=datetime.utcnow().date())
    last_updated = Column(DateTime, default=datetime.utcnow())
    ip_address = Column(String(15))

    def __init__(self, visits=0, date=None, last_updated=None, ip_address=None):  # Dodajte ip_address kao argument
        self.visits = visits
        self.date = date or datetime.utcnow().date()
        self.last_updated = last_updated or datetime.utcnow()
        self.ip_address = ip_address  # Postavite vrednost ip_address
