from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app=Flask(__name__)
app.secret_key='zR0pu1dXbAOhlC-sRX5SzQ'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///sqlite.db'
db=SQLAlchemy(app)
bcrypt=Bcrypt(app)

from target import routes

db.create_all()