from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from target.config import Config

db=SQLAlchemy()
bcrypt=Bcrypt()
mail = Mail()

def create_app(config_class=Config):
    app=Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)

    from target.users.routes import users
    from target.posts.routes import posts
    from target.main.routes import main
    from target.errors.handlers import errors
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    with app.app_context():
        # create new instance of db or brings old db.
        db.create_all()
    
    return app