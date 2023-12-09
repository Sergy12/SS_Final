from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = 'database.db'

action = {
    0: 'Successful login',
    1: 'Unsuccessful login',
    2: 'Successful register',
    3: 'Unsuccessful register',
    4: 'User logout',
    5: 'Note added',
    6: 'Note deleted'
}

def create_app():

    app = Flask(__name__)
    app.config['SECRET_KEY'] = 's3-cr3t-ll4ve¿'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Note

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

def create_database(app):

    if not path.exists('instance/'+DB_NAME):
        with app.app_context():
            db.create_all()
            print('Created Database')