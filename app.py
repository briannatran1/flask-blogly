"""Blogly application."""

import os

from flask import Flask, render_template, request, redirect
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User

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
    image_url = request.form["image_url"]

    user = User(first_name=first_name,
                last_name=last_name, image_url=image_url)

    db.session.add(user)
    db.session.commit()

    return redirect('/users')


@app.get('/users/<int:user_id>')
def show_user_info(user_id):
    """Show information about the specific user"""

    user = User.query.get_or_404(user_id)

    return render_template('user_details.html',
                           user=user)


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
