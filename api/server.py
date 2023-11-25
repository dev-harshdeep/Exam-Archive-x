from flask import Flask, render_template, jsonify ,send_file,url_for
import json
from collections import OrderedDict

import os
import pathlib

import requests
from flask import Flask, session, abort, redirect, request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
import io
import fitz  # PyMuPDF
from PIL import Image
import base64



data = []
with open('output.json', 'r') as file:
    data = json.load(file)

cources = []
for i in range(0, len(data)):
    cources.append(data[i]['Course'])
import os

def list_files_in_directory(directory_path):
    file_list = []
    
    # Check if the directory exists
    if os.path.exists(directory_path):
        # Iterate through all the files and subdirectories in the given directory
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_list.append(file)
    else:
        print(f"The directory '{directory_path}' does not exist.")
        print(file_list)
    return file_list

# Example usage:
directory_path = "pdfs"
files = list_files_in_directory(directory_path)
print("No of files :",len(files))
# print(cources)


def searchFile(filter):
    arr=[]
    for file in files:
        if filter in file:
            arr.append(file)
    return arr


app = Flask(__name__)
app.secret_key = "ExamArchive.com"
cources = []


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
GOOGLE_CLIENT_ID = "1021957323011-mhbqnueds5ju8mvk1pala345f43arai8.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)


Authorised = ['shivanshsharma8899@gmail.com','abc@gmail.com','pqr@gmail.com']


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" in session:
            if session["email"] in Authorised:            
                return function()
        return abort(401) 
    return wrapper

@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

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





@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")





@app.route("/protected_area")
@login_is_required
def protected_area():
    return f"Hello {session['name']}! <br/> <a href='/logout'><button>Logout</button></a>"

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/archive")
def archive():
    return render_template('courseSelector.html')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.route('/getCourses', methods=['GET'])
def get_data():
    cources = []
    for i in range(0, len(data)):
        cources.append(data[i]['Course'])

    return jsonify(cources)


@app.route('/getSem/<cid>')
def getSem(cid):

    ordered_keys = list(OrderedDict.fromkeys(
        key for d in data[int(cid)]['data'] for key in d))

    return jsonify(ordered_keys)
    # return jsonify(data[int(cid)])


@app.route('/SemSelect/<cid>')
def selectSem(cid):
    return render_template('semselect.html')


@app.route('/subSelect/<cid>/<sem>')
def selectSub(cid, sem):
    print(cid, sem)
    return render_template('subselect.html')


@app.route('/getSub/<cid>/<sem>')
def getSub(cid, sem):
    print("Recievedd")
    # print(data[int(cid)]['data'])
    print(data[int(cid)]['data'])
    sanitized_sem = sem.replace("%20", " ")  # Convert "%20" to spaces
    print(sanitized_sem)
    for sem in data[int(cid)]['data']:
        if sanitized_sem in sem:
            print(sem[sanitized_sem])
            return sem[sanitized_sem]

    return jsonify(data[int(cid)])

@app.route('/getPapers/<code>')
def getPapers(code):
    return jsonify(searchFile(code))


@app.route("/showPapers/<code>")
def showPapers(code):
    return render_template('showPaper.html',code=code)

@app.route("/admin/select-questions")
def selectQuestions():
    return render_template('selectQuestions.html')
    

@app.route('/download/<pdf_filename>')
def download_pdf(pdf_filename):
    pdf_path = f'pdfs/{pdf_filename}'
    return send_file(pdf_path, as_attachment=True)







# //////////////////////////////////////////////////////////////////////////////////////////////////////////


def pdf_to_images(pdf_data):
    pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
    images = []

    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        image_list = page.get_pixmap()
        img = Image.frombytes("RGB", [image_list.width, image_list.height], image_list.samples)
        images.append(img)

    pdf_document.close()
    return images

def stitch_images_vertically(images):
    widths, heights = zip(*(i.size for i in images))
    max_width = max(widths)
    total_height = sum(heights)

    new_image = Image.new('RGB', (max_width, total_height))

    y_offset = 0
    for img in images:
        new_image.paste(img, (0, y_offset))
        y_offset += img.size[1]

    return new_image


@app.route('/pdfUpload', methods=['GET', 'POST'])
def pdf_upload():
    if request.method == 'POST':
        pdf_file = request.files.get('pdf_file')

        if not pdf_file:
            return "No PDF file provided", 400

        try:
            pdf_data = pdf_file.read()
            pdf_images = pdf_to_images(pdf_data)
            long_image = stitch_images_vertically(pdf_images)

            image_stream = io.BytesIO()
            long_image.save(image_stream, format='PNG')
            image_stream.seek(0)

            # Encode the image data to base64 for the URL parameter
            encoded_image_data = base64.b64encode(image_stream.read()).decode('utf-8')

            # Trigger the result message in the template
            return render_template('selectQuestions.html', image_data=encoded_image_data)

        except Exception as e:
            return f"Error processing the PDF file: {str(e)}", 500

    return render_template('pdfUpload.html')


@app.route('/resultPage')
def result_page():
    image_data = request.args.get('image_data')

    if not image_data:
        return "No image data provided", 400

    # Decode the image data from base64
    decoded_image_data = base64.b64decode(image_data)

    # Pass the decoded image data to the template
    return render_template('resultPage.html', image_data=decoded_image_data)

# //////////////////////////////////////////////////////////////////////////////////////////////////////////




if __name__ == "__main__":
    # app.run(host='172.16.15.201', port=5000)
    app.run(debug=True)
