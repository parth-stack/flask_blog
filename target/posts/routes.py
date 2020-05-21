from flask import render_template,request,redirect,url_for,flash,session,abort
from flask import Blueprint
from target import db
from target.models import User,Post
from target.posts.forms import PostForm

posts = Blueprint('posts', __name__)

@posts.route("/post/<string:post_id>",methods=['GET','POST'],defaults={'action': None})
@posts.route("/post/<string:post_id>/<string:action>",methods=['GET','POST'])
def post_route(post_id,action):
    if 'user' in session:
        if post_id=='new' and action==None:
            form = PostForm()
            if request.method=='POST' and form.validate_on_submit():
                post = Post(title=form.title.data, content=form.content.data, author=User.query.filter_by(username=session['user']['username']).first())
                db.session.add(post)
                db.session.commit()
                flash('Your post has been created!', 'success')
                return redirect(url_for('main.initial'))
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
                    return redirect(url_for('posts.post_route', post_id=post.id))
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
                return redirect(url_for('main.initial'))
            else:
                abort(404)
        else:
            abort(404)
    else:
        post = Post.query.get_or_404(post_id)
        return render_template('post.html', post=post)
