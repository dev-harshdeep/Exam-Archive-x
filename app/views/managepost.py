from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, current_app
from markdown2 import markdown
from models.posts import Post
from models.database import db
from models.sessions import Session
from models.threads import Thread
from views.checksession import check_session

manage_post_bp = Blueprint('managepost', __name__)


@manage_post_bp.route('/postmanager')  
def show_pending_posts():
    pending_posts = Post.query.filter_by(Approved=0).all()
    for post in pending_posts:
        post.Content = markdown(post.Content)
    return render_template('manage-post.html', pending_posts=pending_posts)

@manage_post_bp.route('/manageaction', methods=["POST"])
def manage_action():
    user, admin_rights = check_session()
    current_app.logger.info("Admin Rights: %s", admin_rights)  
    current_app.logger.info("User Rights: %s", user.id)  
    
    data = request.json
    current_app.logger.info(data)

    action = data.get('action')
    post_id = data.get('postId')
    current_app.logger.info(action)

    post = Post.query.get(post_id)

    if post:
        if action == 'approve':
            post.Approved = 1
            thread = Thread(PostID=post.PostID, IsLock=False)
            db.session.add(thread)
        elif action == 'unapprove':
            post.Approved = -1

        post.ApprovedBy = user.id
        db.session.commit()
        
        # Return response with an additional flag indicating approval action
        return jsonify({'message': 'Action processed successfully', 'reload': action == 'approve'}), 200
    else:
        return jsonify({'error': 'Post not found'}), 404

