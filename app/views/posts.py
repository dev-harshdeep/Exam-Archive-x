from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session,jsonify
from models.posts import Post
from models.database import db
from models.sessions import Session
from models.threads import Thread
from models.category import Category
from models.categorypost import CategoryPost
# from .models import Post, Category, CategoryPost
# from models.category import Category
from views.checksession import check_session
# from markdown2 import markdown
import mistune
posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/<category>')
def index(category=''):
    # Fetch all posts from the database that belong to the specified category
    user, admin_rights = check_session()
    
    per_page = 5
    category_id = Category.query.filter_by(CategoryName=category).first().CategoryID
    
    # Query distinct post IDs associated with the specified category
    post_ids = CategoryPost.query.filter_by(category_id=category_id).with_entities(CategoryPost.post_id).distinct().all()
    post_ids = [post_id for post_id, in post_ids]
    
    # Fetch paginated posts based on the distinct post IDs
    posts = Post.query.filter(Post.PostID.in_(post_ids)).filter_by(Approved=1).paginate(per_page=per_page)
    
    for post in posts.items:
        post.Content = mistune.markdown(post.Content)
        # Fetch the thread associated with the post
        post.thread = Thread.query.filter_by(PostID=post.PostID).first()
        commentTime = post.TimeStamp
        # dt_object = datetime.strptime(post.TimeStamp, '%Y-%m-%d %H:%M:%S')
        post.commentTime = commentTime.strftime('%B,%d %Y')

    return render_template('posts.html', posts=posts, user=user, category=category )




@posts_bp.route('/load-more')
def load_more_posts():
    page = request.args.get('page', 1, type=int)  # Get the page number from the request query parameters
    per_page = 5  # Number of posts to load per page
    category_name = request.args.get('category')  # Get the category name from the request query parameters

    # Fetch category ID based on the category name
    category = Category.query.filter_by(CategoryName=category_name).first()
    if category:
        category_id = category.CategoryID

        # Query distinct post IDs associated wip.strftime('%B,%d %Y')

# Format the datetime object into your desired formatth the specified category
        post_ids = CategoryPost.query.filter_by(category_id=category_id).with_entities(CategoryPost.post_id).distinct().all()
        post_ids = [post_id for post_id, in post_ids]

        # Fetch paginated posts based on the distinct post IDs
        posts = Post.query.filter(Post.PostID.in_(post_ids)).filter_by(Approved=1).paginate(page=page, per_page=per_page, error_out=False)

        # Check if there are more posts available
        has_next = posts.has_next
        for post in posts.items:
            post.Content = mistune.markdown(post.Content)
            # Fetch the thread associated with the post
            
            post.thread = Thread.query.filter_by(PostID=post.PostID).first()
            # dt_object = datetime.strptime(, '%Y-%m-%d %H:%M:%S')
            commentTime = post.TimeStamp
            # dt_object = datetime.strptime(post.TimeStamp, '%Y-%m-%d %H:%M:%S')
            post.commentTime = commentTime.strftime('%B,%d %Y')
        # Prepare posts data for JSON response
        posts_data = [{
            'UserID': post.UserID,
            'Content': post.Content,
            'TimeStamp': post.TimeStamp,
            'DifficultyLevel': post.DifficultyLevel,
            'ThreadID': post.thread.ThreadID
        } for post in posts.items]

        return jsonify({'posts': posts_data, 'has_next': has_next})
    else:
        return jsonify({'error': 'Category not found'})





@posts_bp.route('/submit/<category>', methods=['POST'])
def submit_post(category):
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
        db.session.add(new_post)

        # Commit the changes to the database to generate the PostID
        db.session.commit()

        # Now you can access the PostID from the new_post object
        post_id = new_post.PostID

        # Create a new CategoryPost object with the provided data
        new_cat_post = CategoryPost(
            category_id=Category.query.filter_by(CategoryName=category).first().CategoryID,
            post_id=post_id
        )

        # Add the new category-post relationship to the database session
        db.session.add(new_cat_post)

        # Commit the changes to the database
        db.session.commit()
        return('Post submitted successfully', 'success')
        
    else:
        flash('Session expired or invalid', 'error')
        
    # Redirect to the homepage
    return jsonify({'posts': 'something something'})







 
@posts_bp.route('/categories', methods=['GET', 'POST'])
def categories():
    if request.method == 'POST':
        category_name = request.form['category_name']
        if category_name:
            # Check if category name already exists in the database
            existing_category = Category.query.filter_by(CategoryName=category_name).first()
            if existing_category:
                # If category already exists, redirect back to categories page with a message
                return render_template('categories.html', categories=Category.query.all(), error_message="Category already exists.")
            else:
                # If category does not exist, add it to the database
                new_category = Category(CategoryName=category_name)
                db.session.add(new_category)
                db.session.commit()
                return redirect(url_for('posts.categories'))
    categories = Category.query.all()
    return render_template('categories.html', categories=categories)
