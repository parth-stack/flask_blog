from flask import render_template,request,redirect,url_for,flash,session
import json,secrets,os
from werkzeug.utils import secure_filename
from target import app,db,bcrypt
from target.models import User,Post
from target.forms import RegisterForm,LoginForm,UpdateForm



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
            session['user']={'username':user.username,'email':user.email}
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
                session['user']={'username':user.username,'email':user.email}
                flash('Logged in ',category='success')
                return redirect(url_for('initial'))
            else:
                flash('Login Error',category='danger')
        return render_template("login.html",form=form)
        
@app.route("/logout")
def logout_route():
    if 'user' in session:
        session.pop('user')
        flash('Logged out ', 'success')
    else:
        flash('not in session ', 'danger')
    return redirect(url_for('initial'))

@app.route("/dashboard",methods=['GET','POST'])
def dashboard_route():
    
    def save_picture(form_picture):
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(form_picture.filename)
        picture_fn = random_hex + f_ext
        picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
        form_picture.save(picture_path)
        return picture_fn
        
    if 'user' in session:
        form=UpdateForm()
        current_user = User.query.filter_by(username=session['user']['username']).first()
        image_file=url_for('static',filename='profile_pics/' + current_user.image_file)
        if request.method=='POST' and form.validate():
            if form.picture.data:
                current_user.image_file = save_picture(form.picture.data)
            current_user.username = form.username.data
            current_user.email = form.email.data
            db.session.commit()
            flash('Your account has been updated!', 'success')
            return redirect(url_for('dashboard_route'))
        elif request.method=='GET':
            form.username.data = current_user.username
            form.email.data = current_user.email
        return render_template("dashboard.html",form=form,image_file=image_file)
