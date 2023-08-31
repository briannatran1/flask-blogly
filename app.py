"""Blogly application."""

import os

from flask import Flask, render_template, request, redirect
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, Tag, PostTag, DEFAULT_IMAGE_URL

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL", 'postgresql:///blogly')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)


@app.get('/')
def show_homepage():
    """Show a list of all users"""
    return redirect('/users')


@app.get('/users')
def show_users():
    """Show a list of all users"""

    # Add info from db
    data = User.query.all()

    return render_template('user_listing.html',
                           users=data)

# USERS ROUTES


@app.get('/users/new')
def show_add_user_form():
    """Shows an add form for new users"""
    return render_template('user_form.html')


@app.post('/users/new')
def handle_add_user_form():
    """Process new user form and redirect to user listing"""
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    image_url = request.form.get("image_url", None)

    user = User(first_name=first_name,
                last_name=last_name, image_url=image_url)

    db.session.add(user)
    db.session.commit()

    return redirect('/users')


@app.get('/users/<int:user_id>')
def show_user_info(user_id):
    """Show information about the specific user"""

    user = User.query.get_or_404(user_id)
    posts = user.posts

    return render_template('user_details.html',
                           user=user, posts=posts)


@app.get('/users/<int:user_id>/edit')
def show_edit_user(user_id):
    """Shows edit page for user"""

    user = User.query.get_or_404(user_id)

    return render_template('edit.html',
                           user=user)


@app.post('/users/<int:user_id>/edit')
def processes_form(user_id):
    """Processes edit form and redirects user back to users page"""
    user = User.query.get_or_404(user_id)

    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    image_url = request.form["image_url"] or DEFAULT_IMAGE_URL

    user.first_name = first_name
    user.last_name = last_name
    user.image_url = image_url

    db.session.commit()

    return redirect('/users')


@app.post('/users/<int:user_id>/delete')
def delete_user(user_id):
    """Deletes the user"""
    user = User.query.get_or_404(user_id)

    user.query.delete()
    db.session.commit()

    return redirect('/')

# POST ROUTES


@app.get('/users/<int:user_id>/posts/new')
def show_add_post_form(user_id):
    """Show form to add post for this user"""
    user = User.query.get_or_404(user_id)

    return render_template('new_post.html', user=user)


@app.post('/users/<int:user_id>/posts/new')
def handle_new_post_form(user_id):
    """Handle add form and redirect to user detail page"""
    user = User.query.get_or_404(user_id)

    title = request.form["title"]
    content = request.form["content"]

    post = Post(title=title, content=content, user=user)  # user_id = user.id

    # add flash message for post success

    db.session.add(post)
    db.session.commit()

    return redirect(f'/users/{user_id}')


@app.get('/posts/<int:post_id>')
def show_post(post_id):
    """Shows user a post"""
    post = Post.query.get_or_404(post_id)
    user = post.user

    return render_template('post_details.html',
                           post=post,
                           user=user)


@app.get('/posts/<int:post_id>/edit')
def show_edit_post_form(post_id):
    """Shows form to edit a post and redirects user back to user detail page if canceled"""
    post = Post.query.get_or_404(post_id)
    user = post.user

    return render_template('edit_post.html',
                           post=post,
                           user=user)


@app.post('/posts/<int:post_id>/edit')
def handle_edit_post(post_id):
    """Processes editing of a post. Redirects back to the post page"""
    post = Post.query.get_or_404(post_id)

    post.title = request.form['title']
    post.content = request.form['content']

    # success message => flash

    db.session.commit()

    return redirect(f'/posts/{post_id}')


@app.post('/posts/<int:post_id>/delete')
def delete_post(post_id):
    """Deletes the specified post"""
    post = Post.query.get_or_404(post_id)
    user = post.user

    db.session.delete(post)
    db.session.commit()

    return redirect(f'/users/{user.id}')
