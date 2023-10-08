import pyrebase
from pymongo import MongoClient
from flask import Flask, session, request, url_for, redirect, render_template
import os
from werkzeug.utils import secure_filename
from var import *

app = Flask(__name__)
app.secret_key = "kahsdkfvcoljwbflbwgi3ur1234jhmbags"

client = MongoClient(mongostr, serverSelectionTimeoutMS=60000)

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

admins = []
admin_mails = []
db = client["Food"]

Admin = iter(db["admin"].find())
for records in Admin:
    admins.append(records['acnt_local_id'])
    admin_mails.append(records['mail_id'])

print(admins)
print(admin_mails)

# Set the upload folder
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return redirect('/login')

app.route('/ticket')
def ticket():
    return render_template('ticket.html')
        
        

@app.route('/admin')
def admin():
    user_token = session.get('user_token')
    if user_token:
        if auth.get_account_info(user_token)['users'][0]['email'] in admin_mails:
            return render_template('admin.html')

@app.route('/admin_ticket')
def admin_ticket():
    user_token = session.get('user_token')
    if user_token:
        if auth.get_account_info(user_token)['users'][0]['email'] in admin_mails:
            return render_template('admin_ticket.html')

# Signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        referral_code = request.form['referral']

        try:
            user = auth.create_user_with_email_and_password(email, password)
            user_data = {
                'email': email,
                'referral_code': email[:5]+str(random.randint(1000,9999)),
                'points': 0
            }

            # Insert the user data into MongoDB
            db["users"].insert_one(user_data)
            db["users"].update_one({"referral_code": referral_code}, {"$inc": {"points": 10}})
            return redirect(url_for('login'))

        except Exception as e:
            error_message = str(e)
            return render_template('signup.html', error_message=error_message)
    return render_template('signup.html')


# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session['user_token'] = user['idToken']
            if user['localId'] in admins:
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('dashboard'))
        except Exception as e:
            error_message = str(e)
            return render_template('login.html', error_message=error_message)
    return render_template('login.html')

# Dashboard page
@app.route('/dashboard')
def dashboard():
    user_token = session.get('user_token')
    # print(user_email)
    print(user_token)
    if user_token:
        try:
            # Use the user_token to fetch user-specific data from Firebase Realtime Database
            user_email = auth.get_account_info(user_token)['users'][0]['email']
            return render_template('dashboard.html', user_email=user_email)
        except Exception as e:
            print("Error fetching user data:", e)
            return redirect(url_for('login'))
    return redirect(url_for('login'))

app.config['UPLOAD_FOLDER'] = 'uploads'

# Create the upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

app = Flask(__name__)

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Check if any files were uploaded
        if 'image_files' not in request.files:
            return "No files selected for upload"

        # Get the list of uploaded files
        image_files = request.files.getlist('image_files')

        # Create a list to store file paths
        file_paths = []

        for image_file in image_files:
            # Check if the file is empty
            if image_file.filename == '':
                return "One or more selected files are empty"

            # Generate a secure filename to avoid naming conflicts
            filename = secure_filename(image_file.filename)

            # Save the uploaded file to the 'uploads' folder with a new name
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(file_path)
            file_paths.append(file_path)

        # Now, you can access the list of file paths in the 'file_paths' variable
        # and perform any further processing as needed.

        # For example, you can return the list of file paths as a response
        return f"Uploaded {len(file_paths)} files: {', '.join(file_paths)}"

    return render_template('upload.html')

@app.route('/gallery')
def gallery():
    # Get a list of all uploaded image files in the 'uploads' folder
    uploaded_files = [os.path.join(app.config['UPLOAD_FOLDER'], filename) for filename in os.listdir(app.config['UPLOAD_FOLDER']) if allowed_file(filename)]

    return render_template('gallery.html', uploaded_files=uploaded_files)



@app.route('/logout')
def logout():
    session.pop('user_token', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
