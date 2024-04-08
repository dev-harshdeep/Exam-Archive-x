from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session,jsonify
from models.posts import Post
from models.database import db
from models.sessions import Session
from models.threads import Thread
from views.checksession import check_session
from markdown2 import markdown

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/')
def index():
    # Fetch all posts from the database
    user, admin_rights = check_session()
    
    per_page = 5
    # posts = Post.query.filter_by(Approved=1).all()
    posts = Post.query.filter_by(Approved=1).paginate(per_page=per_page)
    
    for post in posts:
        post.Content = markdown(post.Content)
        # Fetch the thread associated with the post
        post.thread = Thread.query.filter_by(PostID=post.PostID).first()

    return render_template('posts.html', posts=posts, user=user)




@posts_bp.route('/load-more')
def load_more_posts():
    page = request.args.get('page', 1, type=int)  # Get the page number from the request query parameters
    per_page = 5  # Number of posts to load per page

    # Fetch posts for the requested page
    posts = Post.query.filter_by(Approved=1).paginate(page=page, per_page=per_page, error_out=False)
    
    # Check if there are more posts available
    has_next = posts.has_next
    for post in posts:
        post.Content = markdown(post.Content)
        # Fetch the thread associated with the post
        post.thread = Thread.query.filter_by(PostID=post.PostID).first()



    posts_data = [{
        'UserID': post.UserID,
        'Content': markdown(post.Content),
        'TimeStamp':post.TimeStamp,
        'DifficultyLevel':post.DifficultyLevel,
        'ThreadID': post.thread.ThreadID
    } for post in posts.items]



    return jsonify({'posts': posts_data, 'has_next': has_next})


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





