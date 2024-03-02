from flask import Blueprint, render_template, request,abort,url_for

status_bp = Blueprint('status', __name__)

@status_bp.route("/status")
def show_status():
    # Get status and message from URL query parameters
    status = request.args.get('status')
    message = request.args.get('message')

    # Check if status is provided
    if not status:
        abort(400, "Status is missing in the URL")

    # Determine GIF based on status
    if status.lower() == 'success':
        gif_url = url_for('static', filename='success.gif')
    elif status.lower() == 'failure':
        gif_url = url_for('static', filename='error.gif')
    else:
        abort(400, "Invalid status provided in the URL")

    # Render the template with the appropriate variables
    return render_template("status.html", status=status, message=message, gif_url=gif_url)
