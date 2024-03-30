from flask import redirect, url_for , Blueprint , request ,  render_template
# from checksession import check_session
from views.checksession import check_session
home_bp = Blueprint("home", __name__)

@home_bp.route("/", methods=['GET', 'POST'])
def index():
    user, admin_rights = check_session()  # Call check_session to get user and admin rights

    if request.method == 'POST':
        query = request.form.get('search_query')
        if query:
            return redirect(url_for('search_bp.search_page', query=query))
    # return render_template("index.html")
    return render_template("index.html", user=user)
