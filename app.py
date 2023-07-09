import io
import os
import json 
from OpenSSL import SSL

from flask import (
    Flask, flash,
    redirect, request, Response,
    render_template, 
    session, url_for, 
    abort, send_from_directory
)
from flask_cors import CORS

from google_auth_oauthlib.flow import Flow
from oauth import OAuth # , API_Token, API_Authorizer

from google_services.upload import GG_DriveFileUploader
from google_services import authentication 
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from werkzeug.utils import secure_filename
from presentation_utils import SlidesUtils
# Text-to-speech
from gtts import gTTS
import tts

# Configure for objects:
with open('config.json') as f:
    config = json.load(f)


# Create a Flask app object
app = Flask("Slides Teaching System")
app.secret_key = "sts"  #it is necessary to set a password when dealing with OAuth 2.0
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
CORS(app, origins=["https://docs.google.com"])
# context = SSL.Context(SSL.TLSv1_2_METHOD)


# context.use_privatekey_file("server.key")
# context.use_certificate_file("server.crt")
# context.use_privatekey_file("server.key")
# context.use_certificate_file("server.crt")

# Initialize object
flow = Flow.from_client_secrets_file(
    client_secrets_file = config["client_secrets_file"],
    scopes = config['scopes'],
    redirect_uri = config["redirect_uri"]
)
oauth = OAuth()
loginer = authentication.Loginer(flow, config)# GoogleAPI()
slide_ulity, file_uploader = [None]*2


@app.route("/login")  #the page where the user can login
def login():
    # Get the authorization url and state from the GoogleAPI object
    authorization_url = loginer.authorize(oauth) # state 
 
    # Redirect to the authorization url
    return redirect(authorization_url)

@app.route("/callback")  #this is the page that will handle the callback process meaning process after the authorization
def callback():
    loginer.verify_oauth_token_and_set_user_info(oauth)
    # Redirect to the protected area
    global file_uploader, slide_ulity
    slide_ulity = SlidesUtils(flow)
    file_uploader = GG_DriveFileUploader(flow)
    # print_cmt(flow.credentials)

        
    # print(get_speaker_notes("1spmrPZeOJbSwttjYyo2-MTa2R9Vkx9IV67iXvRiYjFI", "g22f0867fb07_7_49"))
    return redirect(url_for("welcome"))

@app.route("/logout")  
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/")  
def index():
    return "Hello World <a href='/login'><button>Login</button></a>"

@app.route("/welcome")  
@oauth.login_is_required
def welcome():
    return f"Welcome, {session['name']}! <br/> <a href='/logout'><button>Logout</button></a>"  

@app.route('/upload_slide')
def upload_slides():
    return render_template('upload_slide.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file'] 
    if file and (file.filename.endswith('.pptx') or file.filename.endswith('.ppt')):   
        upload_state = file_uploader.upload(file)
        presentation_url =  upload_state.get('id') #get('webViewLink')[]

        print(upload_state)
        
        return render_template(
            'play.html', 
            url=presentation_url,
            # slide_url=presentation_url + "#slide=id.p1" # Thêm dòng này
        )


@app.route('/record-audio')
def audio_rec():
    return render_template("rec_audio.html") # app.send_static_file('rec_audio.html') 


@app.route('/save-record', methods=['POST'])
def save_record():
    # check if the post request has the file part
    if not file_uploader:
        flash('No file part')
        return abort(401)
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    file_uploader.upload(file)
    return '<h1>Success</h1>'


@app.route('/read_content')
def read_content():
    return render_template('tts.html')

@app.route('/read', methods=['POST'])
def read():
    data = tts.read_content()
    return Response(data, mimetype='audio/mpeg')



@app.route('/open_url')
def open_url():
    return render_template(
        'slides.html'
    )

# 1BJtDZ7XGHc0IKvDGC3nFPhmFh_x9Hcc6Dsw9ubx_e5s

# 1spmrPZeOJbSwttjYyo2-MTa2R9Vkx9IV67iXvRiYjFI,  g22f0867fb07_7_49
# 1fUcWO-DTGb9Xlb5W6nICbK_pwHXMhmqUIipJrvToyKQ
if __name__ == "__main__":
    # app.run(ssl_context=('cert.pem', 'key.pem'))
    app.run(debug= True, ssl_context=('./server.crt', './server.key'))

# Test the function with a sample presentation id
# print(get_speaker_notes("12SQU9Ik-ShXecJoMtT-LlNwEPiFR7AadnxV2KiBXCnE"))