from flask import Blueprint, redirect, session, abort, request, current_app , url_for
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from pip._vendor import cachecontrol
import google.auth.transport.requests
import os
import requests
from dotenv import load_dotenv
import pathlib
from functools import wraps

load_dotenv() 

auth_bp = Blueprint('auth', __name__)
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
client_secrets_file =os.path.join(pathlib.Path(__file__).parent.parent, os.environ.get("CLIENT_SECRETS_FILE"))
# print(client_secrets_file)

if not GOOGLE_CLIENT_ID or not client_secrets_file:
    raise ValueError("GOOGLE_CLIENT_ID and CLIENT_SECRETS_FILE must be set in environment variables.")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)

Authorised = ['dev.harshjoshi@gmail.com', 'shivanshsharma8899@gmail.com', 'abc@gmail.com', 'pqr@gmail.com']

@auth_bp.route("/login")
def login():
    session.clear()  # Clear the session before initiating login
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    current_app.logger.info(f"Redirecting to Google for login. State: {state}")
    return redirect(authorization_url)


def login_is_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        global Authorised
        Authorised = ['dev.harshjoshi@gmail.com', 'shivanshsharma8899@gmail.com', 'abc@gmail.com', 'pqr@gmail.com']

        print("Current session:", session)
        if "google_id" in session:
            print("Check 1")
            if session["email"] in Authorised:
                print("Auth check 1")
                return function(*args, **kwargs)
        print("Logging you out here")
        return redirect("/logout")
    return wrapper

@auth_bp.route("/callback")
def callback():
    current_app.logger.info("Callback received.")

    # Skip debugger requests
    if request.args.get("__debugger__") == "yes":
        return "Debugger requests are not allowed in the callback."

    flow.fetch_token(authorization_response=request.url)

    # Log the state to check if it's received correctly
    current_app.logger.info(f"Received state: {request.args.get('state')}")
    current_app.logger.info(f"Session state: {session.get('state')}")

    # Ensure "state" exists in both session and request.args before accessing them
    if "state" not in session or "state" not in request.args or session["state"] != request.args["state"]:
        current_app.logger.error("State mismatch in callback.")
        # abort(500)  # State does not match!
        redirect("/logout")
    credentials = flow.credentials
    current_app.logger.info(f"Credentials obtained: {credentials}")
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
        return redirect("/admin/dashboard")
    return redirect("/logout")

def authenticate_user(token):
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    return id_info.get("email"), id_info.get("sub")

def store_user_session(email, google_id, token):
    session["email"] = email
    session["google_id"] = google_id
    session["google_token"] = token

def clear_user_session():
    session.clear()

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")
