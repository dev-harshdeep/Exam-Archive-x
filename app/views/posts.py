from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.posts import Post
from models.database import db
from models.sessions import Session
from views.checksession import check_session
from markdown2 import markdown

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/')
def index():
    # Fetch all posts from the database
    user, admin_rights = check_session()
    
    posts = Post.query.all()
    for post in posts:
        post.Content = markdown(post.Content)

    return render_template('posts.html', posts=posts,user=user)

@posts_bp.route('/submit', methods=['POST'])
def submit_post():
    # Retrieve post content from the form
    post_content = request.form.get('post_content')
    
    # Get the current timestamp
    current_time = datetime.utcnow()
    
    # Get the session token from the session
    session_token = session.get('session_token')
    
    # Query the Session table to get the user_id based on the session_token
    session_info = Session.query.filter_by(sid=session_token).first()
    
    if session_info:
        user_id = session_info.user_id
        
        # Create a new post object with the provided data
        new_post = Post(
            UserID=user_id,
            Content=post_content,
            TimeStamp=current_time,
            DifficultyLevel=1
        )
        
        # Add the new post to the database session
        db.session.add(new_post)
        
        # Commit the changes to the database
        db.session.commit()
        flash('Post submitted successfully', 'success')
        
    else:
        flash('Session expired or invalid', 'error')
        
    # Redirect to the homepage
    return redirect(url_for('posts.index'))

