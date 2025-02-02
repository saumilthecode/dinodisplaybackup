from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import time
import random
import string
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = '/var/www/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route to upload a new drawing
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    if file and allowed_file(file.filename):
        # Generate a unique filename using timestamp and random string
        timestamp = str(int(time.time()))  # Current time as a string
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=6))  # Random string of 6 chars
        filename = f"{timestamp}_{random_string}_{secure_filename(file.filename)}"
        
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200
    return jsonify({'error': 'Invalid file type'}), 400

# Route to list all uploaded images
@app.route('/images', methods=['GET'])
def list_images():
    files = os.listdir(UPLOAD_FOLDER)
    # Filter only allowed image extensions
    images = [f for f in files if allowed_file(f)]
    return jsonify(images)

# Route to serve the images from the /uploads folder
@app.route('/uploads/<filename>', methods=['GET'])
def serve_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Admin panel to view and remove images
@app.route('/admin', methods=['GET'])
def admin_console():
    # List all images in the upload folder
    files = os.listdir(UPLOAD_FOLDER)
    images = [f for f in files if allowed_file(f)]
    return render_template('admin.html', images=images)

# Route to remove an image (Admin only)
@app.route('/delete/<filename>', methods=['POST'])
def delete_image(filename):
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({'message': f'{filename} removed successfully'}), 200
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

