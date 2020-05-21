from flask import render_template,request,redirect,url_for,flash,session,abort
import json,secrets,os
from werkzeug.utils import secure_filename
from flask_mail import Message
from target import app,db,bcrypt,mail
from target.models import User,Post
from target.forms import RegisterForm,LoginForm,UpdateForm,PostForm,RequestResetForm,ResetPasswordForm


@app.route("/")
@app.route("/home")
def initial():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template("index.html",posts=posts)

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

@app.route("/post/<string:post_id>",methods=['GET','POST'],defaults={'action': None})
@app.route("/post/<string:post_id>/<string:action>",methods=['GET','POST'])
def post_route(post_id,action):
    if 'user' in session:
        if post_id=='new' and action==None:
            form = PostForm()
            if request.method=='POST' and form.validate_on_submit():
                post = Post(title=form.title.data, content=form.content.data, author=User.query.filter_by(username=session['user']['username']).first())
                db.session.add(post)
                db.session.commit()
                flash('Your post has been created!', 'success')
                return redirect(url_for('initial'))
            return render_template('create_post.html',form=form, legend='New Post')
        elif post_id.isnumeric():
            if action==None:
                post = Post.query.get_or_404(post_id)
                return render_template('post.html', post=post)
            elif action=='update':
                post = Post.query.get_or_404(post_id)
                if post.author.email != session['user']['email']:
                    abort(403)
                form = PostForm()
                if form.validate_on_submit():
                    post.title = form.title.data
                    post.content = form.content.data
                    db.session.commit()
                    flash('Your post has been updated!', 'success')
                    return redirect(url_for('post_route', post_id=post.id))
                elif request.method == 'GET':
                    form.title.data = post.title
                    form.content.data = post.content
                return render_template('create_post.html', form=form, legend='Update Post')
            elif action=='delete':
                post = Post.query.get_or_404(post_id)
                if post.author.email != session['user']['email']:
                    abort(403)
                db.session.delete(post)
                db.session.commit()
                flash('Your post has been deleted!', 'success')
                return redirect(url_for('initial'))
            else:
                abort(404)
        else:
            abort(404)
    else:
        post = Post.query.get_or_404(post_id)
        return render_template('post.html', post=post)



@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    def send_reset_email(user):
        token = user.get_reset_token()
        msg = Message('Password Reset Request',sender='noreply@demo.com',recipients=[user.email])
        msg.body = f'''To reset your password, visit the following link:
        {url_for('reset_token', token=token, _external=True)}
        If you did not make this request then simply ignore this email and no changes will be made.
        '''
        mail.send(msg)
    
    if 'user' in session:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if 'user' in session:
        return redirect(url_for('initial'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', form=form)