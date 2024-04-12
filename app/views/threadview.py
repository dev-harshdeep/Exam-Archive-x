from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session , current_app,jsonify
from models.posts import Post
from models.database import db
from models.sessions import Session
from models.comments import Comments
from models.threads import Thread
from views.checksession import check_session
import mistune
from models.commentlikes import Commentlikes  # Import your CommentLikes model



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
            # Fetch the number of likes and dislikes for the comment
            comment.likes = Commentlikes.query.filter_by(PostID=comment.CommentID, Action=1).count()
            comment.dislikes = Commentlikes.query.filter_by(PostID=comment.CommentID, Action=-1).count()
            
            # Check if the user is logged in
            if user:
                # Check if the current user has liked or disliked the comment
                liked = Commentlikes.query.filter_by(UserID=user.id, PostID=comment.CommentID, Action=1).first()
                disliked = Commentlikes.query.filter_by(UserID=user.id, PostID=comment.CommentID, Action=-1).first()
                comment.has_liked = True if liked else False
                comment.has_disliked = True if disliked else False
            else:
                # If the user is not logged in, set both has_liked and has_disliked to False
                comment.has_liked = False
                comment.has_disliked = False

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
    


@threads_bp.route('/handle-likes/<postId>/<action>', methods=['POST'])
def handle_likes(postId, action):
    user, admin_rights = check_session()

    if request.method == 'POST':
        # Check if the action is either 'like' or 'dislike' or 'removeopinion'
        if action in ['like', 'dislike', 'removeopinion']:
            # Check if the action is valid
            if action == 'like':
                # Check if the user already has an opinion on this post
                existing_opinion = Commentlikes.query.filter_by(UserID=user.id, PostID=postId).first()
                if existing_opinion:
                    existing_opinion.Action = 1  # Update the existing opinion to like
                else:
                    # Create a new entry in the database
                    new_opinion = Commentlikes(UserID=user.id, PostID=postId, Action=1)
                    db.session.add(new_opinion)
                db.session.commit()

            elif action == 'dislike':
                # Check if the user already has an opinion on this post
                existing_opinion = Commentlikes.query.filter_by(UserID=user.id, PostID=postId).first()
                if existing_opinion:
                    existing_opinion.Action = -1  # Update the existing opinion to dislike
                else:
                    # Create a new entry in the database
                    new_opinion = Commentlikes(UserID=user.id, PostID=postId, Action=-1)
                    db.session.add(new_opinion)
                db.session.commit()

            elif action == 'removeopinion':
                # Check if the user already has an opinion on this post
                existing_opinion = Commentlikes.query.filter_by(UserID=user.id, PostID=postId).first()
                if existing_opinion:
                    db.session.delete(existing_opinion)  # Remove the existing opinion from the database
                    db.session.commit()

            # Return success message
            return 'Action successfully performed'

    # Handle invalid actions or other HTTP methods
    return 'Invalid action or method', 400
