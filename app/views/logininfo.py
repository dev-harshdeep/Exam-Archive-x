# app/logininfo.py

from flask import Blueprint, render_template, session

logininfo_blueprint = Blueprint('logininfo', __name__)

@logininfo_blueprint.route('/logininfo')
def logininfo():
    # Retrieve session information
    user_id = session.get('user_id')
    email = session.get('email')
    # You can add more session data as needed

    # Pass session information to the frontend template
    return render_template('logininfo.html', user_id=user_id, email=email)
