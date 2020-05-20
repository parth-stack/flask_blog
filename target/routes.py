from flask import render_template,request,redirect,url_for,flash,session
import json
from target import app,db,bcrypt
from target.models import User,Post
from target.forms import RegisterForm,LoginForm


with open('target/config.json','r') as c:
    config_json = json.load(c)

with open('target/posts.json','r') as p:
    posts_json = json.load(p)

@app.route("/")
@app.route("/home")
def initial():
    return render_template("index.html",urls=config_json["urls"],posts=posts_json)

@app.route("/register",methods=['GET','POST'])
def register():
    if 'user' in session:
        return redirect(url_for('initial'))
    else:
        form=RegisterForm() 
        if request.method=='POST' and form.validate():
            hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data,password=hashed_password,email=form.email.data)
            db.session.add(user)
            db.session.commit()
            session['user']=user.username
            flash('Registerd as '+form.username.data,category='success')
            return redirect(url_for('login'))
        return render_template("register.html",form=form)

@app.route("/login",methods=['GET','POST'])
def login():
    if 'user' in session:
        return redirect(url_for('initial'))
    else:
        form=LoginForm()
        if request.method=='POST' and form.validate():
            user = User.query.filter_by(email=form.email.data).first()
            if(user) and bcrypt.check_password_hash(user.password,form.password.data):
                session['user']=user.username
                flash('Logged in ',category='success')
                return redirect(url_for('initial'))
            else:
                flash('Login Error',category='danger')
        return render_template("login.html",form=form)
        
@app.route("/logout")
def logout_route():
    session.pop('user')
    return redirect(url_for('initial'))

@app.route("/dashboard",methods=['GET','POST'])
def dashboard_route():
    return session['user']