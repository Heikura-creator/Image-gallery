import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, session
from werkzeug.utils import secure_filename

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Flask App Setup
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'supersecretkey'  # Needed for flash messages

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Dummy credentials (for now)
USERNAME = 'admin'
PASSWORD = 'wordpass'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            flash('Logged in successfully!')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials.')
            return redirect(request.url)
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Logged out.')
    return redirect(url_for('index'))

# Helper to check file extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Homepage – Show gallery
@app.route('/')
def index():
    sort = request.args.get('sort', 'newest')  # default is newest

    image_files = os.listdir(app.config['UPLOAD_FOLDER'])
    image_paths = [
        (img, os.path.getmtime(os.path.join(app.config['UPLOAD_FOLDER'], img)))
        for img in image_files
    ]

    # Sort based on modification time
    if sort == 'oldest':
        sorted_images = sorted(image_paths, key=lambda x: x[1])
    else:
        sorted_images = sorted(image_paths, key=lambda x: x[1], reverse=True)

    sorted_filenames = [img[0] for img in sorted_images]

    # Pagination (12 per page)
    page = int(request.args.get('page', 1))
    per_page = 12
    start = (page - 1) * per_page
    end = start + per_page
    paginated_images = sorted_filenames[start:end]
    total_pages = (len(sorted_filenames) + per_page - 1) // per_page

    return render_template('index.html', images=paginated_images, page=page, total_pages=total_pages, sort=sort)

# Upload page
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not session.get('logged_in'):
        flash('Please log in to upload images.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['image']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            flash('Image uploaded successfully!')
            return redirect(url_for('index'))
        else:
            flash('Invalid file type. Allowed: png, jpg, jpeg, gif, webp')
            return redirect(request.url)

    return render_template('upload.html')

# Delete image
@app.route('/delete/<filename>', methods=['POST'])
def delete_image(filename):
    if not session.get('logged_in'):
        flash("You must be logged in to delete images.")
        return redirect(url_for('index'))

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        flash(f"Deleted {filename}")
    else:
        flash(f"File {filename} not found.")

    return redirect(url_for('index'))

# Serve image file directly (optional)
@app.route('/image/<filename>')
def view_image(filename):
    return render_template('image.html', filename=filename)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
