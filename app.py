from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from functools import wraps
import bcrypt
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'home_builder_secret_key_2024'

# Configuration - Image upload only
UPLOAD_FOLDER = 'static/uploads/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload folders if not exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static/uploads/videos', exist_ok=True)

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Create admin table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Create projects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            main_image TEXT,
            video_file TEXT,
            video_url TEXT,
            category TEXT,
            bedrooms INTEGER,
            bathrooms INTEGER,
            garage INTEGER,
            area_size TEXT,
            floors INTEGER,
            location TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create project_images table for gallery images
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS project_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            image_name TEXT NOT NULL,
            FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    ''')
    
    # Create leads table (for quote form submissions)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create default admin user
    cursor.execute('SELECT * FROM admin WHERE username = ?', ('Admin',))
    if not cursor.fetchone():
        hashed_password = bcrypt.hashpw('Admin@123'.encode('utf-8'), bcrypt.gensalt())
        cursor.execute('INSERT INTO admin (username, password) VALUES (?, ?)', 
                      ('Admin', hashed_password))
        print("Default admin user created: Admin / Admin@123")
    
    conn.commit()
    conn.close()

init_db()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ===================== ROUTES =====================

@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # Get latest 6 projects - no category filter
    cursor.execute('SELECT * FROM projects ORDER BY created_at DESC LIMIT 6')
    projects = cursor.fetchall()
    conn.close()
    return render_template('index.html', projects=projects)

@app.route('/projects')
def projects():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # Get Upcoming projects
    cursor.execute('SELECT * FROM projects WHERE LOWER(category) = LOWER("Upcoming") ORDER BY created_at DESC')
    upcoming_projects = cursor.fetchall()
    # Get Completed projects
    cursor.execute('SELECT * FROM projects WHERE LOWER(category) = LOWER("Completed") ORDER BY created_at DESC')
    completed_projects = cursor.fetchall()
    conn.close()
    return render_template('projects.html', upcoming_projects=upcoming_projects, completed_projects=completed_projects)

@app.route('/project/<int:id>')
def project_detail(id):
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM projects WHERE id = ?', (id,))
    project = cursor.fetchone()
    
    # Get gallery images for this project
    images = []
    if project:
        cursor.execute('SELECT * FROM project_images WHERE project_id = ?', (id,))
        images = cursor.fetchall()
    
    conn.close()
    
    if not project:
        flash('Project not found')
        return redirect('/projects')
    return render_template('project_detail.html', project=project, images=images)

# ===================== SOLUTIONS PAGES =====================

@app.route('/solutions/new-construction')
def solution_new_construction():
    return render_template('solution_new.html')

@app.route('/solutions/renovation')
def solution_renovation():
    return render_template('solution_renovation.html')

@app.route('/solutions/design-planning')
def solution_design():
    return render_template('solution_design.html')

# ===================== QUOTE FORM (LEADS) =====================

@app.route('/submit-quote', methods=['POST'])
def submit_quote():
    # Get form data - use exact names from HTML
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    message = request.form.get('message', '').strip()
    
    if not name or not email or not phone:
        flash('Please fill in all required fields.')
        return redirect('/#contact')
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO leads (name, email, phone, message)
        VALUES (?, ?, ?, ?)
    """, (name, email, phone, message))
    conn.commit()
    conn.close()
    
    flash('Thank you! Your quote request has been submitted. We will contact you soon.')
    return redirect('/#contact')

# ===================== ADMIN ROUTES =====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admin WHERE LOWER(username) = LOWER(?)', (username,))
        admin = cursor.fetchone()
        conn.close()
        
        if admin and bcrypt.checkpw(password.encode('utf-8'), admin['password']):
            session['admin_id'] = admin['id']
            session['username'] = admin['username']
            return redirect('/dashboard')
        else:
            flash('Invalid username or password')
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/dashboard')
@login_required
def dashboard():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM projects ORDER BY created_at DESC')
    projects = cursor.fetchall()
    conn.close()
    return render_template('dashboard.html', projects=projects, username=session.get('username'))

@app.route('/add-project', methods=['GET', 'POST'])
@login_required
def add_project():
    if request.method == 'POST':
        title = request.form.get('title', '')
        description = request.form.get('description', '')
        category = request.form.get('category', 'Upcoming')
        
        bedrooms = request.form.get('bedrooms', '')
        bathrooms = request.form.get('bathrooms', '')
        garage = request.form.get('garage', '')
        area_size = request.form.get('area_size', '').strip()
        floors = request.form.get('floors', '')
        location = request.form.get('location', '').strip()
        
        bedrooms = int(bedrooms) if bedrooms else None
        bathrooms = int(bathrooms) if bathrooms else None
        garage = int(garage) if garage else None
        floors = int(floors) if floors else None
        
        # Handle main image - FILE UPLOAD ONLY
        main_image = None
        image_file = request.files.get('main_image')
        
        if image_file and image_file.filename:
            if allowed_file(image_file.filename):
                filename = secure_filename(image_file.filename)
                image_path = os.path.join(UPLOAD_FOLDER, filename)
                image_file.save(image_path)
                main_image = filename
            else:
                flash('Invalid image file type. Allowed: png, jpg, jpeg, webp')
                return redirect('/add-project')
        
        # Handle video - file or URL
        video_file = None
        video_url = None
        
        if 'video_file' in request.files:
            video = request.files['video_file']
            if video and video.filename:
                if allowed_file(video.filename):
                    filename = secure_filename(video.filename)
                    video.save(os.path.join('static/uploads/videos', filename))
                    video_file = filename
                else:
                    flash('Invalid video file type.')
                    return redirect('/add-project')
        
        if not video_file:
            video_url = request.form.get('video_url', '').strip()
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO projects (title, description, main_image, video_file, video_url, category, bedrooms, bathrooms, garage, area_size, floors, location) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, description, main_image, video_file, video_url, category, bedrooms, bathrooms, garage, area_size, floors, location))
        
        # Get the last inserted project ID
        project_id = cursor.lastrowid
        
        # Handle gallery images - up to 9 additional images
        gallery_images = request.files.getlist('gallery_images')
        
        if gallery_images:
            # Limit to max 9 gallery images
            max_gallery = 9
            for i, gallery_file in enumerate(gallery_images[:max_gallery]):
                if gallery_file and gallery_file.filename:
                    if allowed_file(gallery_file.filename):
                        filename = secure_filename(gallery_file.filename)
                        # Add unique suffix to avoid filename conflicts
                        name, ext = os.path.splitext(filename)
                        filename = f"{name}_{project_id}_{i}{ext}"
                        image_path = os.path.join(UPLOAD_FOLDER, filename)
                        gallery_file.save(image_path)
                        
                        # Insert into project_images table
                        cursor.execute(
                            'INSERT INTO project_images (project_id, image_name) VALUES (?, ?)',
                            (project_id, filename)
                        )
        
        conn.commit()
        conn.close()
        
        flash('Project added successfully!')
        return redirect('/dashboard')
    
    return render_template('add_project.html')

@app.route('/delete-project/<int:id>')
@login_required
def delete_project(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Get project to delete associated files
    cursor.execute('SELECT main_image, video_file FROM projects WHERE id = ?', (id,))
    project = cursor.fetchone()
    if project:
        # Delete main image file
        if project[0]:
            image_path = os.path.join(UPLOAD_FOLDER, project[0])
            if os.path.exists(image_path):
                os.remove(image_path)
        # Delete video file
        if project[1]:
            video_path = os.path.join('static/uploads/videos', project[1])
            if os.path.exists(video_path):
                os.remove(video_path)
    
    # Delete gallery images
    cursor.execute('SELECT image_name FROM project_images WHERE project_id = ?', (id,))
    gallery_images = cursor.fetchall()
    for img in gallery_images:
        image_path = os.path.join(UPLOAD_FOLDER, img[0])
        if os.path.exists(image_path):
            os.remove(image_path)
    
    # Delete from project_images table
    cursor.execute('DELETE FROM project_images WHERE project_id = ?', (id,))
    
    # Delete project
    cursor.execute('DELETE FROM projects WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Project deleted successfully!')
    return redirect('/dashboard')

@app.route('/admin/leads')
@login_required
def admin_leads():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM leads ORDER BY created_at DESC')
    leads = cursor.fetchall()
    conn.close()
    return render_template('admin_leads.html', leads=leads, username=session.get('username'))

if __name__ == '__main__':
    app.run()
