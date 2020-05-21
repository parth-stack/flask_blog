from flask import render_template,request,redirect,url_for,flash,session,Blueprint
from target import db,bcrypt
from target.models import User,Post
from target.users.forms import RegisterForm,LoginForm,UpdateForm,RequestResetForm,ResetPasswordForm
from target.users.utils import save_picture,send_reset_email

users = Blueprint('users', __name__)

@users.route("/register",methods=['GET','POST'])
def register():
    if 'user' in session:
        return redirect(url_for('main.initial'))
    else:
        form=RegisterForm() 
        if request.method=='POST' and form.validate():
            hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data,password=hashed_password,email=form.email.data)
            db.session.add(user)
            db.session.commit()
            session['user']={'username':user.username,'email':user.email}
            flash('Registerd as '+form.username.data,category='success')
            return redirect(url_for('users.login'))
        return render_template("register.html",form=form)

@users.route("/login",methods=['GET','POST'])
def login():
    if 'user' in session:
        return redirect(url_for('main.initial'))
    else:
        form=LoginForm()
        if request.method=='POST' and form.validate():
            user = User.query.filter_by(email=form.email.data).first()
            if(user) and bcrypt.check_password_hash(user.password,form.password.data):
                session['user']={'username':user.username,'email':user.email}
                flash('Logged in ',category='success')
                return redirect(url_for('main.initial'))
            else:
                flash('Login Error',category='danger')
        return render_template("login.html",form=form)
        
@users.route("/logout")
def logout_route():
    if 'user' in session:
        session.pop('user')
        flash('Logged out ', 'success')
    else:
        flash('not in session ', 'danger')
    return redirect(url_for('main.initial'))

@users.route("/dashboard",methods=['GET','POST'])
def dashboard_route():
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
            return redirect(url_for('users.dashboard_route'))
        elif request.method=='GET':
            form.username.data = current_user.username
            form.email.data = current_user.email
        return render_template("dashboard.html",form=form,image_file=image_file)

@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if 'user' in session:
        return redirect(url_for('main.initial'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', form=form)

@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if 'user' in session:
        return redirect(url_for('main.initial'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', form=form)