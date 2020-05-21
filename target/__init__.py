from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail

app=Flask(__name__)
app.secret_key='zR0pu1dXbAOhlC-sRX5SzQ'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///sqlite.db'
db=SQLAlchemy(app)
bcrypt=Bcrypt(app)
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = "parthsharma.asia@gmail.com"
app.config['MAIL_PASSWORD'] = "q6w6e6r6t6y"
mail = Mail(app)

from target import routes

db.create_all()