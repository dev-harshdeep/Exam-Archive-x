from flask import Flask, render_template


############################# Libraries Imported for google Login ############################

import os
import pathlib

import requests
from flask import Flask, session, abort, redirect, request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests

# ////////////////////////////// main_app ///////////////////////////////

app = Flask(__name__)
app.secret_key = "ExamArchive.com"

@app.route("/")
def home():
    return render_template('index.html')



################################## CODE FOR GOOGLE LOG IN ######################################




os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# ------------> Google Client Id generated from Google Oauth for our end <---------------------

GOOGLE_CLIENT_ID = "1021957323011-mhbqnueds5ju8mvk1pala345f43arai8.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)



# ---------------> MAKING  THE LIST OF AUTHORISEZED EMAILS OF ADMINS <----------------------

Authorised = ['shivanshsharma8899@gmail.com','abc@gmail.com','pqr@gmail.com']




# ----------------> User Log_in will verified in this function <---------------------

def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper



# ----------------> LogIn function <---------------------

@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


#  -------------------> here all login google account will get compared with the google database via sending an request
#  if all credential matches the user will be redirect to protected_area() for secure login process <--------------------- 

@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["email"] = id_info.get("email")
    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    if session["email"] in Authorised:
        return redirect("/protected_area")
    return redirect("/logout")





# ----------------> after log_in when user reaches to protected_area() if a user log out their account 
# all their data will be cleared and they will be redirected to home() again <-----------------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")




# -------------------> after succesfull log_In user will come to protected area <--------------------------

@app.route("/protected_area")
@login_is_required
def protected_area():
    return f"Hello {session['name']}! <br/> <a href='/logout'><button>Logout</button></a>"

    
   



# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////





############################## Running app in debug mode ##############################

if __name__ == "__main__":
    app.run(debug=True)
