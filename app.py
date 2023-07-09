import io
import os
import json 
from OpenSSL import SSL

from flask import (
    Flask, flash,
    redirect, request, Response,
    render_template, 
    session, url_for, 
    abort, send_from_directory, jsonify
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

from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import InputRequired
from wtforms import FileField
from pymongo import MongoClient
import json
import pymongo

# Configure for objects:
with open('config.json') as f:
    config = json.load(f)
from flask_pymongo import PyMongo


app = Flask(__name__, static_folder='public')
app.secret_key = "sts"  #it is necessary to set a password when dealing with OAuth 2.0
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
CORS(app, origins=["https://docs.google.com"])
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'public/files'
password = os.environ.get("MONGODB_PWD")
app.config['MONGO_URI'] = f"""mongodb+srv://annpt17:{password}@cluster0.awppk3c.mongodb.net/Soft_Eng"""
mongo = PyMongo(app)

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
# 1fUcWO-DTGb9Xlb5W6nICbK_pwHXMhmqUIipJrvToyK

# Test the function with a sample presentation id
# print(get_speaker_notes("12SQU9Ik-ShXecJoMtT-LlNwEPiFR7AadnxV2KiBXCnE"))



# Cấu hình biến môi trường trong Flask
# app.config['MONGODB_URI'] = 'mongodb://localhost:27017/'
# app.config['MONGODB_DB'] = 'admin'
# #Connect MongoDB
# client = MongoClient(app.config['MONGODB_URI'])
# db = client[app.config['MONGODB_DB']]
# try:
#     #Kiểm tra kết nối
#     server_info = client.server_info()
#     print("Connect to MongoDB successful!")
# except Exception as e:
#     print("Connect to MongoDB failed:", e)
# mongo = pymongo.MongoClient(app.config['MONGODB_URI'])


# def create_course():
#     print("class names are added")
#     return "success"
# def get_classes(final_classes_json):
#     coursenames = json.loads(final_classes_json)['course']
#     return jsonify(coursenames)
    # fetch classes by username
    # return [
    #     "Class 1",...
    # ]
# @app.route('/api/createCourse/<username>', methods=['PUT'])
# def createcourse(username):
#     course = request.json['course']
#     if course and username and request.method == 'PUT':
#         mongo.db.course.find_one_and_update({'username': username}, {'$set': { 'course': course}})
#         result = create_course()
#         return jsonify(result)

#     else:
#         print("Not Found")
#         return not_found()



#upload file;
class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

@app.route('/upload.html', methods=['GET',"POST"])
def home():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data # First grab the file
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename))) # Then save the file
        return render_template('view-slide.html')
    return render_template('upload.html', form=form)
#route

# @app.route('/view-slide/<slide_id>')
# def view_slide(slide_id):
#     slide = db.slides.find_one({'_id': ObjectId(slide_id)})

#     if slide:
#         return render_template('view-slide.html', slide=slide)
#     else:
#         return 'Slide not found'
@app.route("/m")
def ind4ex():
    return render_template('m.html')
@app.route("/")
def indexno():
    return render_template('index.html')

@app.route("/record-audio.html")
def recordaudio():
    return render_template('record-audio.html')
@app.route("/view-slide.html")
def viewslide():
    return render_template('view-slide.html')
@app.route("/gg-sign-in.html")
def ggsignin():
    return render_template('gg-sign-in.html')
@app.route("/create-course.html")
def createcoursevip():
    return render_template('create-course.html')
@app.route("/location.html")
def location():
    return render_template('location.html')
@app.route("/offer.html")
def offer():
    return render_template('offer.html')
@app.route("/slide-creating.html")
def slidecreating():
    return render_template('slide-creating.html')


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found' + request.url 
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp

if __name__ == "__main__":
    # app.run(ssl_context=('cert.pem', 'key.pem'))
    app.run(debug= True)