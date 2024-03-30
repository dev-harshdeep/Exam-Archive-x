from flask import Blueprint, render_template, redirect, url_for, flash, request
from models.user import User, db, AdminRole

admin_management_blueprint = Blueprint('admin_management', __name__)

@admin_management_blueprint.route('/admin_management')
def admin_management():
    # Retrieve all users with their associated admin roles
    users = User.query.all()
    admin_roles = {}
    for user in users:
        if user.admin_role_id:
            admin_role = AdminRole.query.get(user.admin_role_id)
            admin_roles[user.admin_role_id] = admin_role
    return render_template('admin_management.html', users=users, admin_roles=admin_roles)



@admin_management_blueprint.route('/make_admin/<int:user_id>', methods=['POST'])
def make_admin(user_id):
    user = User.query.get(user_id)
    if user:
        # Check if the user is already an admin
        if not user.is_admin:
            # If the user is not an admin, set is_admin to True
            user.is_admin = True
            db.session.commit()

            # Check if the user already has an AdminRole
            if not user.admin_role_id:
                # Create a new AdminRole for the user
                admin_role = AdminRole()
                db.session.add(admin_role)
                db.session.commit()

                # Assign the admin role ID to the user
                user.admin_role_id = admin_role.id
                db.session.commit()

                flash('User {} is now an admin.'.format(user.email), 'success')
            else:
                flash('User already has an admin role.', 'info')
        else:
            flash('User is already an admin.', 'info')
    else:
        flash('User not found.', 'error')

    return redirect(url_for('admin_management.admin_management'))


@admin_management_blueprint.route('/remove_admin/<int:user_id>', methods=['POST'])
def remove_admin(user_id):
    user = User.query.get(user_id)
    if user:
        user.is_admin = False
        db.session.commit()
        flash('Admin privileges removed from {}.'.format(user.email), 'success')
    else:
        flash('User not found.', 'error')
    return redirect(url_for('admin_management.admin_management'))

@admin_management_blueprint.route('/edit_permissions/<int:user_id>', methods=['POST'])
def edit_permissions(user_id):
    user = User.query.get(user_id)
    if user:
        # Check if an admin role exists for the user
        admin_role = None
        if user.admin_role_id:
            admin_role = AdminRole.query.get(user.admin_role_id)

        # If no admin role exists, create a new one
        if not admin_role:
            admin_role = AdminRole()
            db.session.add(admin_role)
            user.admin_role_id = admin_role.id

        # Update admin permissions based on form submission
        admin_role.can_access_backup = 'can_access_backup' in request.form
        admin_role.can_edit_posts = 'can_edit_posts' in request.form
        admin_role.can_edit_courses = 'can_edit_courses' in request.form
        admin_role.can_upload_pdfs = 'can_upload_pdfs' in request.form
        admin_role.can_manage_admins = 'can_manage_admins' in request.form

        db.session.commit()
        flash('Admin permissions updated for {}.'.format(user.email), 'success')
    else:
        flash('User not found.', 'error')

    return redirect(url_for('admin_management.admin_management'))
