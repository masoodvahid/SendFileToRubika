import subprocess
import sys
import os

def install_requirements():
    """Install the required packages from requirements.txt."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError as e:
        print(f"Failed to install packages: {e}")
        sys.exit(1)

# Check if requirements.txt exists and install the packages
if os.path.exists('requirements.txt'):
    install_requirements()
else:
    print("requirements.txt not found. Please create the file with the necessary dependencies.")
    sys.exit(1)

from flask import Flask, request, render_template, jsonify, redirect, url_for, session
from rubpy import Client
import mimetypes
import requests
import os
import time
from tqdm import tqdm

app = Flask(__name__,
            static_url_path='',
            static_folder='static',
            )
app.secret_key = 'a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6'  # Replace with your generated secret key

# Replace with your actual channel ID
channel_id = 'c0CAr8k042a92f4b45c05e41810475f0'

# Initialize statistics
total_files_sent = 0
total_uploaded_size = 0
total_downloaded_size = 0

# Simple password for demonstration purposes
PASSWORD = 'your_password_here'

def get_file_type(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        if mime_type.startswith('video'):
            return 'video'
        elif mime_type.startswith('audio'):
            return 'music'
        elif mime_type.startswith('image'):
            return 'photo'
        elif mime_type == 'application/pdf' or mime_type.startswith('application'):
            return 'document'
        elif mime_type.startswith('audio'):
            return 'voice'
    return None

def update_statistics(file_size, is_upload=True):
    global total_files_sent, total_uploaded_size, total_downloaded_size
    total_files_sent += 1
    if is_upload:
        total_uploaded_size += file_size
    else:
        total_downloaded_size += file_size
    print(f"Total files sent: {total_files_sent}")
    print(f"Total uploaded size: {total_uploaded_size / (1024 ** 3):.2f} GB")
    print(f"Total downloaded size: {total_downloaded_size / (1024 ** 3):.2f} GB")

def append_caption(caption):
    additional_text = "\n\n به ما بپیوندید  👇👇👇 \nhttps://rubika.ir/joinc/BHBGGHAA0WBNZWVNSKGNXYJLTXMTCPKM"
    return caption + additional_text

def upload_file_with_progress(client, channel_id, file_path, caption):
    file_size = os.path.getsize(file_path)
    file_type = get_file_type(file_path)
    if not file_type:
        return "Unsupported file type"

    caption = append_caption(caption)

    try:
        with tqdm(total=file_size, unit='B', unit_scale=True, desc='Uploading') as pbar:
            if file_type == 'video':
                client.send_video(channel_id, file_path, caption=caption)
            elif file_type == 'music':
                client.send_music(channel_id, file_path, caption=caption)
            elif file_type == 'photo':
                client.send_photo(channel_id, file_path, caption=caption)
            elif file_type == 'voice':
                client.send_voice(channel_id, file_path, caption=caption)
            elif file_type == 'document':
                client.send_document(channel_id, file_path, caption=caption)
            pbar.update(file_size)
        update_statistics(file_size, is_upload=True)
        return f"{file_type.capitalize()} sent successfully"
    except Exception as e:
        return f"Error sending {file_type}: {e}"

def check_local_access():
    if request.remote_addr != '127.0.0.1':
        return jsonify({'message': 'Access denied. Only local machine access is allowed.'}), 403

def login_required(f):
    def wrap(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return "Invalid password", 403
    return render_template('login.html')

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    check_local_access()
    file = request.files['file']
    caption = request.form['caption']
    if file:
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)
        with Client("Rubika", display_welcome=False) as rubika:
            message = upload_file_with_progress(rubika, channel_id, file_path, caption)
        os.remove(file_path)
        return jsonify({'message': message})
    return jsonify({'message': 'No file selected!'})

@app.route('/upload_url', methods=['POST'])
@login_required
def upload_url():
    check_local_access()
    file_url = request.form['file_url']
    caption = request.form['caption']
    temp_file_path = 'temp_file'
    try:
        response = requests.get(file_url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        with open(temp_file_path, 'wb') as file, tqdm(total=total_size, unit='B', unit_scale=True, desc='Downloading') as pbar:
            for data in response.iter_content(1024):
                file.write(data)
                pbar.update(len(data))
        with Client("Rubika", display_welcome=False) as rubika:
            message = upload_file_with_progress(rubika, channel_id, temp_file_path, caption)
        os.remove(temp_file_path)
        update_statistics(total_size, is_upload=False)
        return jsonify({'message': message})
    except Exception as e:
        return jsonify({'message': f"Error downloading file: {e}"})

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True, use_reloader=False)
