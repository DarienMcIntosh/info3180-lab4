import os
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, session, abort
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from app.models import UserProfile
from app.forms import LoginForm
from werkzeug.security import check_password_hash
from app.forms import LoginForm, UploadForm
from flask import send_from_directory



###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")


@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload():
    # Instantiate your form class
    form = UploadForm()

    # Validate file upload on submit
    if form.validate_on_submit():
        # Get file data and save to your uploads folder
        photo = form.photo.data
        filename = secure_filename(photo.filename)
        
        # Use the upload folder path from config, relative to project root
        # not relative to app directory
        uploads_dir = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'])
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
            
        # Save the file
        photo.save(os.path.join(uploads_dir, filename))

        flash('File Saved', 'success')
        return redirect(url_for('files'))

    # Flash any form errors
    flash_errors(form)
    return render_template('upload.html', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()

    # change this to actually validate the entire form submission
    # and not just one field
    if form.username.data:
        # Get the username and password values from the form.
        username = form.username.data
        password = form.password.data

        # Query database for a user based on the username submitted
        user = db.session.execute(db.select(UserProfile).filter_by(username=username)).scalar()

        # Using your model, query database for a user based on the username
        # and password submitted. Remember you need to compare the password hash.
        # You will need to import the appropriate function to do so.
        # Then store the result of that query to a `user` variable so it can be
        # passed to the login_user() method below.

        # Check if user exists and password matches
        if user is not None and check_password_hash(user.password, password):
            # Gets user id, load into session
            login_user(user)

        # Flash a success message
            flash('Login successful!', 'success')
            
            # Redirect to the upload form
            return redirect(url_for("upload"))
        else:
            # If authentication fails, flash an error message
            flash('Username or Password is incorrect.', 'danger')
            
    # Flash any form validation errors
    flash_errors(form)

    return render_template("login.html", form=form)

@app.route('/files')
@login_required
def files():
    # Get list of images from uploads folder
    images = get_uploaded_images()
    
    # Render the template with the list of images
    return render_template('files.html', images=images)

@app.route('/uploads/<filename>')
def get_image(filename):
    """Serve uploaded images"""
    uploads_dir = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'])
    return send_from_directory(uploads_dir, filename)


# Helper function to get list of uploaded files
def get_uploaded_images():
    # Use path relative to project root, not app directory
    uploads_dir = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'])
    
    # Get filenames of images in the uploads folder
    images = []
    if os.path.exists(uploads_dir):
        for filename in os.listdir(uploads_dir):
            # Only add files with allowed extensions (jpg, jpeg, png)
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                images.append(filename)
    
    return images

# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return db.session.execute(db.select(UserProfile).filter_by(id=id)).scalar()

###
# The functions below should be applicable to all Flask apps.
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404
