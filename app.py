"""Blogly application."""

import os

from flask import Flask, render_template, request, redirect
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post

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


@app.get('/users/new')
def show_add_user_form():
    """Shows an add form for new users"""
    return render_template('user_form.html')


@app.post('/users/new')
def handle_add_user_form():
    """Process new user form and redirect to user listing"""
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    image_url = request.form["image_url"] or None

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
    image_url = request.form["image_url"]

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

@app.get('/users/<int:user_id>/posts/new')
def show_add_post_form(user_id):
    """Show form to add post for this user"""
    user = User.query.get_or_404(user_id)

    return render_template('new_post.html', user=user)

@app.post('/users/<int:user_id>/posts/new')
def handle_new_post_form(user_id):
    """Handle add form and redirect to user detail page"""
    user = User.query.get_or_404(user_id)

    title=request.form["title"]
    content=request.form["content"]

    post = Post(title=title, content=content, user_id=user.id)

    db.session.add(post)
    db.session.commit()

    return redirect(f'/users/{user_id}')