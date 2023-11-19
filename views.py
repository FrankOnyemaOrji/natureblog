from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models.base_model import User, Comment, Post, Message
from create_app import db

views = Blueprint('views', __name__)


@views.route('/')
def index():
    posts = Post.query.all()
    return render_template('index.html', user=current_user, posts=posts)


@views.route('/about')
def about():
    return render_template('about.html', user=current_user)


@views.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        sender = request.form.get('sender')
        email = request.form.get('email')
        message = request.form.get('message')

        if not sender:
            flash('Name is required!', category='error')
        elif not email:
            flash('Email is required!', category='error')
        elif not message:
            flash('Message is required!', category='error')
        else:
            messages = Message(sender=sender, email=email, message=message)
            db.session.add(messages)
            db.session.commit()
            flash('Message sent!', category='success')
            return redirect(url_for('views.index'))
    return render_template('contact.html')


@views.route('/createPost', methods=['GET', 'POST'])
@login_required
def createPost():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        if not title:
            flash('Title is required!', category='error')
        elif not content:
            flash('Content is required!', category='error')
        else:
            posts = Post(title=title, content=content, author=current_user.id)
            db.session.add(posts)
            db.session.commit()
            flash('Post created!', category='success')
            return redirect(url_for('views.index'))
    return render_template('createPost.html', user=current_user.username)


@views.route('/deletePost/<id>')
@login_required
def deletePost(id):
    posts = Post.query.filter_by(id=id).first()
    if not posts:
        flash('Post does not exist!', category='error')
    elif current_user.id != posts.author:
        flash('You do not have permission to delete this post!', category='error')
    else:
        db.session.delete(posts)
        db.session.commit()
        flash('Post deleted!', category='success')
    return redirect(url_for('views.index'))


@views.route('/editPost/<id>', methods=['GET', 'POST'])
@login_required
def editPost(id):
    edit_post = Post.query.get(id)
    if not edit_post:
        flash('Post does not exist!', category='error')
    elif current_user.id != edit_post.author:
        flash('You do not have permission to edit this post!', category='error')
    else:
        if request.method == 'POST':
            edit_post.title = request.form.get('title')
            edit_post.content = request.form.get('content')

            if not edit_post.title:
                flash('Title is required!', category='error')
            elif not edit_post.content:
                flash('Content is required!', category='error')
            else:
                db.session.commit()
                flash('Post edited!', category='success')
                return redirect(url_for('views.index'))
        return render_template('editPost.html', user=current_user.username, edit_post=edit_post)


@views.route('/post/<username>', methods=['GET', 'POST'])
@login_required
def post(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User does not exist!', category='error')
    else:
        posts = Post.query.filter_by(author=user.id).all()
        return render_template('post.html', user=current_user, posts=posts, username=username)


@views.route('/createComment/<id>', methods=['GET', 'POST'])
@login_required
def createComment(id):
    if request.method == 'POST':
        comment_content = request.form.get('comment_content')
        if not comment_content:
            flash('Comment is required!', category='error')
        else:
            comments = Comment(comment_content=comment_content, author=current_user.id, post_id=id)
            db.session.add(comments)
            db.session.commit()
            flash('Comment created!', category='success')
            return redirect(url_for('views.index'))
    post = Post.query.get(id)
    comments = Comment.query.filter_by(post_id=id).all()
    return render_template('comments.html', user=current_user.username, post=post, comments=comments)


@views.route('/deleteComment/<id>')
@login_required
def deleteComment(id):
    comments = Comment.query.filter_by(id=id).first()
    if not comments:
        flash('Comment does not exist!', category='error')
    elif current_user.id != comments.author:
        flash('You do not have permission to delete this comment!', category='error')
    else:
        db.session.delete(comments)
        db.session.commit()
        flash('Comment deleted!', category='success')
    return redirect(url_for('views.index'))


@views.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User does not exist!', category='error')
    else:
        posts = Post.query.filter_by(author=user.id).all()
        comments = Comment.query.filter_by(author=user.id).all()
        return render_template('profile.html', user=current_user, posts=posts, comments=comments, username=username)
