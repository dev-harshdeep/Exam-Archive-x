from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session , current_app,jsonify
from views.checksession import check_session
from models.posts import Post
import mistune
from models.threads import Thread
profile_bp = Blueprint('profile', __name__)

@profile_bp.route("/profile")
def renderprofile():
        user, admin_rights = check_session()

# Get approved posts for the user
        approved_posts = Post.query.filter(Post.UserID == user.id, Post.Approved == 1).all()

        # Get pending posts for the user
        pending_posts = Post.query.filter(Post.UserID == user.id, Post.Approved == 0).all()

        # Get rejected posts for the user
        rejected_posts = Post.query.filter(Post.UserID == user.id, Post.Approved == -1).all()

        for post in approved_posts:
            post.Content = mistune.markdown(post.Content)
            post.thread = Thread.query.filter_by(PostID=post.PostID).first()


        for post in pending_posts:
            post.Content = mistune.markdown(post.Content)

        for post in rejected_posts:
            post.Content = mistune.markdown(post.Content)

        return render_template('profile.html', user=user , admin_rights=admin_rights ,approved_posts=approved_posts,rejected_posts=rejected_posts,pending_posts=pending_posts )






