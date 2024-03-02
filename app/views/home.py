from flask import redirect, url_for , Blueprint , request ,  render_template
home_bp = Blueprint("home", __name__)

@home_bp.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form.get('search_query')
        if query:
            return redirect(url_for('search_bp.search_page', query=query))
    return render_template("index.html")
