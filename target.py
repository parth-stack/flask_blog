from flask import Flask,render_template,request,redirect,url_for,flash
import json
from forms import RegisterForm,LoginForm

with open('config.json','r') as c:
    config_json = json.load(c)

with open('posts.json','r') as p:
    posts_json = json.load(p)

app=Flask(__name__)
app.secret_key='zR0pu1dXbAOhlC-sRX5SzQ'

@app.route("/")
def initial():
    return render_template("index.html",urls=config_json["urls"],posts=posts_json)

@app.route("/register",methods=['GET','POST'])
def register():
    form=RegisterForm() 
    if request.method=='POST' and form.validate(): 
        flash('Registerd as '+form.username.data,category='success')
        flash('Logged in ',category='success')
        return redirect(url_for('initial'))
    return render_template("register.html",form=form)

@app.route("/login",methods=['GET','POST'])
def login():
    form=LoginForm()
    if request.method=='POST' and form.validate():
        flash('Logged in ',category='success')
        return redirect(url_for('initial'))
    return render_template("login.html",form=form)