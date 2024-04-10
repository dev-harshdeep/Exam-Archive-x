from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session , current_app,jsonify
from models.posts import Post
from models.database import db
from models.sessions import Session
from models.comments import Comments
from models.threads import Thread
from views.checksession import check_session
import mistune



threads_bp = Blueprint('threads', __name__)





@threads_bp.route('/thread/<thread_id>', methods=['GET'])
def submit_thread(thread_id):
    # Fetch the thread from the database
    user, admin_rights = check_session()
    thread = Thread.query.get(thread_id)

    if thread:
        # Fetch the post associated with the thread
       

        post = Post.query.get(thread.PostID)
        post.Content = mistune.markdown(post.Content)

        # Fetch comments related to the thread
        comments = Comments.query.filter_by(ThreadId=thread_id).all()
        
        for comment in comments:
            comment.Content = mistune.markdown(comment.Content)
            commentTime = comment.TimeStamp
            # dt_object = datetime.strptime(post.TimeStamp, '%Y-%m-%d %H:%M:%S')
            comment.commentTime = commentTime.strftime('%B,%d %Y')
            if comment.Reply:
                comment.ReplyContent = Comments.query.filter_by(CommentID = comment.Reply).first().Content

        # Render the template with post content and comments
        return render_template("thread.html", post=post, comments=comments ,thread = thread, user=user)
    else:
        # Handle case when thread with given ID doesn't exist
        flash('Thread not found', 'error')
        return redirect(url_for('home')) 
    

@threads_bp.route('/comment/<thread_id>', methods =["post"])
def submit_comment(thread_id):
    # Retrieve the current user session
    user, admin_rights = check_session()

    if user:
        comment_content = request.form.get('comment_content')
        reply_to = request.form.get('replyto')
        current_app.logger.info("replyto")
        current_app.logger.info(reply_to)
        # Save the comment to the database
        if reply_to!='':
            comment = Comments(
            Reply = reply_to,
            ThreadId=thread_id,
            UserID=user.id,  # Assuming user.id contains the ID of the current user
            Content=comment_content,
            TimeStamp=datetime.now()  # Use current timestamp
            )
        else:
            comment = Comments(
            ThreadId=thread_id,
            UserID=user.id,  # Assuming user.id contains the ID of the current user
            Content=comment_content,
            TimeStamp=datetime.now()  # Use current timestamp
            )

        db.session.add(comment)
        db.session.commit()

        # Log the comment submission for debugging purposes
        current_app.logger.info(f"Comment submitted by user {user.id} for thread {thread_id}")

        # Redirect back to the thread page
        return redirect(url_for('threads.submit_thread', thread_id=thread_id))
    else:
        return jsonify({"error":"You are not logged in "})