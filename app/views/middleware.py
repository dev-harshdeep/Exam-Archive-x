# app/middleware.py

from flask import g, redirect, flash
from models.user import User , AdminRole
def check_login():
    """Middleware to check if the user is logged in."""
    if 'user' not in g or not g.user:
        flash('You must be logged in to access this page.', 'error')
        return redirect('/login')

def check_admin():
    """Middleware to check if the user is an admin."""
    if not g.user or not g.user.is_admin:
        flash('You do not have permission to access this page.', 'error')
        return redirect('/')

def check_admin_permissions():
    """Middleware to check the permissions of the admin."""
    if not g.user or not g.user.is_admin:
        flash('You do not have permission to access this page.', 'error')
        return redirect('/')
    else:
        # Example: Check admin permissions and render specific content accordingly
        if g.user.admin_role:
            permissions = {
                'can_access_backup': g.user.admin_role.can_access_backup,
                'can_edit_posts': g.user.admin_role.can_edit_posts,
                'can_edit_courses': g.user.admin_role.can_edit_courses,
                'can_upload_pdfs': g.user.admin_role.can_upload_pdfs,
                'can_manage_admins': g.user.admin_role.can_manage_admins
            }
            return permissions
        else:
            # Handle case where admin role is not defined for the user
            flash('Admin role not defined for the user.', 'error')
            return redirect('/')

def authenticate_user(email, password):
    # Authenticate user
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        g.user = user
        if user.is_admin:
            # Retrieve and set admin permissions
            g.admin_permissions = {
                'can_access_backup': user.admin_role.can_access_backup,
                'can_edit_posts': user.admin_role.can_edit_posts,
                # Add other permissions here
            }
        else:
            # If not an admin, set admin_permissions to None
            g.admin_permissions = None
        return True
    else:
        return False