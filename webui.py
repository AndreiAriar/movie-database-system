from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.urandom(24)  # More secure random secret key
DATABASE = 'mydatabase.db'

# Predefined lists of movies and directors
PREDEFINED_MOVIES = [
    {"title": "The Shawshank Redemption", "director": "Frank Darabont", "year": "1994"},
    {"title": "The Godfather", "director": "Francis Ford Coppola", "year": "1972"},
    {"title": "Pulp Fiction", "director": "Quentin Tarantino", "year": "1994"},
    {"title": "The Dark Knight", "director": "Christopher Nolan", "year": "2008"},
    {"title": "Schindler's List", "director": "Steven Spielberg", "year": "1993"}
]

def get_db_connection():
    """Create a database connection with row_factory for dict-like access."""
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def init_database():
    """Initialize the database with predefined movies if it's empty."""
    try:
        conn = get_db_connection()
        if not conn:
            return False

        # Create movies table if not exists
        conn.execute(''' 
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                director TEXT NOT NULL,
                year TEXT NOT NULL
            )
        ''')
        
        # Updated users table with email field
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')

        # Check if database is empty, then populate with predefined movies
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM movies')
        count = cursor.fetchone()[0]
        
        if count == 0:
            for movie in PREDEFINED_MOVIES:
                conn.execute('INSERT INTO movies (title, director, year) VALUES (?, ?, ?)', 
                             (movie['title'], movie['director'], movie['year']))
        
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
        return False
    finally:
        if conn:
            conn.close()

# Login required decorator
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Home route - List and search movies
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return render_template('index.html', movies=[])

    movies = []
    try:
        if request.method == 'POST':
            search_query = request.form.get('search', '').strip()
            movies = conn.execute(''' 
                SELECT * FROM movies 
                WHERE LOWER(title) LIKE LOWER(?) OR LOWER(director) LIKE LOWER(?)
            ''', ('%' + search_query + '%', '%' + search_query + '%')).fetchall()
        else:
            movies = conn.execute('SELECT * FROM movies').fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        flash('Error retrieving movies', 'error')
    finally:
        conn.close()
    return render_template('index.html', movies=movies, username=session.get('username'))

# Add a new movie
@app.route('/add_movie', methods=['POST'])
@login_required
def add_movie():
    title = request.form.get('Title', '').strip()
    director = request.form.get('Director', '').strip()
    year = request.form.get('Date', '').strip()
    
    if not all([title, director, year]):
        flash('All fields are required', 'error')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return redirect(url_for('index'))

    try:
        conn.execute('INSERT INTO movies (title, director, year) VALUES (?, ?, ?)', 
                     (title, director, year))
        conn.commit()
        flash('Movie added successfully', 'success')
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        flash('Error adding movie', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('index'))

# Update an existing movie
@app.route('/update_movie/<int:id>', methods=['POST'])
@login_required
def update_movie(id):
    title = request.form.get('Title', '').strip()
    director = request.form.get('Director', '').strip()
    year = request.form.get('Date', '').strip()
    
    if not all([title, director, year]):
        flash('All fields are required', 'error')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return redirect(url_for('index'))

    try:
        conn.execute('UPDATE movies SET title = ?, director = ?, year = ? WHERE id = ?', 
                     (title, director, year, id))
        conn.commit()
        flash('Movie updated successfully', 'success')
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        flash('Error updating movie', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('index'))

# Delete a movie
@app.route('/delete_movie/<int:id>')
@login_required
def delete_movie(id):
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return redirect(url_for('index'))

    try:
        conn.execute('DELETE FROM movies WHERE id = ?', (id,))
        conn.commit()
        flash('Movie deleted successfully', 'success')
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        flash('Error deleting movie', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('index'))

# Sign Up Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        if not all([username, email, password, confirm_password]):
            flash('All fields are required', 'error')
            return redirect(url_for('signup'))

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('signup'))
        
        hashed_password = generate_password_hash(password)
        
        try:
            conn = get_db_connection()
            # Check if username or email already exists
            existing_user = conn.execute('SELECT * FROM users WHERE username = ? OR email = ?', 
                                      (username, email)).fetchone()
            if existing_user:
                flash('Username or email already exists', 'error')
                return redirect(url_for('signup'))

            conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', 
                         (username, email, hashed_password))
            conn.commit()
            flash('Account created successfully!', 'success')
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            flash('Error creating account', 'error')
        finally:
            if conn:
                conn.close()
        
        return redirect(url_for('login'))
    return render_template('signup.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        if not email or not password:
            flash('Email and password are required', 'error')
            return redirect(url_for('login'))
        
        conn = get_db_connection()
        try:
            user = conn.execute('SELECT * FROM users WHERE email = ?', 
                              (email,)).fetchone()
            
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                flash('Login successful!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid email or password', 'error')
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            flash('Error during login', 'error')
        finally:
            if conn:
                conn.close()

    return render_template('login.html')

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

# Reset Password Route
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        if not email:
            flash('Please provide an email address', 'error')
            return redirect(url_for('reset_password'))

        conn = get_db_connection()
        try:
            user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
            if user:
                # In a real application, implement password reset email functionality here
                flash('Password reset instructions have been sent to your email', 'success')
            else:
                flash('No account found with that email address', 'error')
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            flash('Error processing request', 'error')
        finally:
            if conn:
                conn.close()

    return render_template('reset_password.html')

# Requirements file for dependencies
def create_requirements_file():
    requirements = """
flask
werkzeug
"""
    with open('requirements.txt', 'w') as f:
        f.write(requirements.strip())

if __name__ == '__main__':
    # Initialize the database with predefined movies
    init_database()
    
    # Create requirements file
    create_requirements_file()
    
    # Run the application
    app.run(debug=True, port=5000)