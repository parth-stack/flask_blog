from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)

app.secret_key='zR0pu1dXbAOhlC-sRX5SzQ'

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///sqlite.db'
db=SQLAlchemy(app)

from target import routes

db.create_all()