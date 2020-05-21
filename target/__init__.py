from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from target.config import Config

app=Flask(__name__)

app.config.from_object(Config)

db=SQLAlchemy(app)
bcrypt=Bcrypt(app)

mail = Mail(app)

from target.users.routes import users
from target.posts.routes import posts
from target.main.routes import main
app.register_blueprint(users)
app.register_blueprint(posts)
app.register_blueprint(main)


db.create_all()