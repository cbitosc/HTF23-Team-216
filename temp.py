from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
import os

app = Flask(__name__)

# Configuration for Flask-PyMongo
app.config["MONGO_URI"] = "mongodb://localhost:27017/image_gallery"
mongo = PyMongo(app)

@app.route('/')
def index():
    return redirect(url_for('upload'))

# Create the upload folder if it doesn't exist
os.makedirs("uploads", exist_ok=True)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Check if any files were uploaded
        if 'image_files' not in request.files:
            return "No files selected for upload"

        # Get the list of uploaded files
        image_files = request.files.getlist('image_files')

        for image_file in image_files:
            # Check if the file is empty
            if image_file.filename == '':
                return "One or more selected files are empty"

            # Save the uploaded file to the 'uploads' folder
            file_path = os.path.join("uploads", image_file.filename)
            image_file.save(file_path)

            # Store image metadata in MongoDB
            mongo.db.images.insert_one({"filename": image_file.filename, "path": file_path})

        # Redirect to the image gallery page
        return redirect(url_for('gallery'))

    return render_template('upload.html')

@app.route('/gallery')
def gallery():
    # Get image metadata from MongoDB
    images = list(mongo.db.images.find())

    return render_template('gallery.html', images=images)

if __name__ == '__main__':
    app.run(debug=True)
