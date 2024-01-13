from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_moment import Moment



# Inicijalizacija SQLAlchemy i Migrate
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # Definisanje rute za login
uploaded_images = UploadSet('images', IMAGES) # Konfiguracija za slike

def create_app():
    app = Flask(__name__)

    # Konfiguracija aplikacije
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///neuron.db'
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['UPLOADED_IMAGES_DEST'] = 'static/images'  # putanja za čuvanje slika
    configure_uploads(app, uploaded_images)

    # Inicijalizacija dodataka sa aplikacijom
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    moment = Moment(app)


    # Import modela mora biti nakon inicijalizacije db
    from .models import User, News, Page
    from .utils import calculate_read_time
    
    # Importovanje i registracija Blueprint-a
    from .blueprints.news.routes import news_bp
    from .blueprints.pages.routes import pages_bp
    from .blueprints.auth.routes import auth_bp
    from .blueprints.admin.routes import admin_bp
    from .blueprints.main import main_bp
    from .blueprints.admin.routes import record_visit

    app.register_blueprint(main_bp)
    app.register_blueprint(news_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.jinja_env.filters['calculate_read_time'] = calculate_read_time
    # User loader za Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('error.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
    # Opcionalno: Dodajte logiku za logovanje greške
        return render_template('error.html'), 500
    
    #Dodavanje funkcije za record visits
    @app.before_request
    def before_request():
        record_visit()


    # Dodavanje funkcije u Jinja2 kontekst
    @app.context_processor
    def context_processor():
        return dict(calculate_read_time=calculate_read_time)
    
    return app
