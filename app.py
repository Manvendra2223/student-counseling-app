from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'

UPLOAD_FOLDER = 'receipts'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# In-memory user storage (for demo)
users = {}

# Admin credentials
admin_credentials = {'admin@example.com': 'admin123'}

# ------------------- HOME -------------------
@app.route('/')
def home():
    return render_template('index.html')

# ------------------- STUDENT SIGNUP -------------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if email in users:
            return "User already exists!"

        users[email] = {'name': name, 'password': password}
        return redirect(url_for('login'))

    return render_template('signup.html')

# ------------------- STUDENT LOGIN -------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email in users and users[email]['password'] == password:
            session['user'] = users[email]['name']
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials"

    return render_template('login.html')

# ------------------- STUDENT DASHBOARD -------------------
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        conn = sqlite3.connect('students.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM students WHERE name = ?", (session['user'],))
        student_data = c.fetchone()
        conn.close()
        return render_template('dashboard.html', user=session['user'], student_data=student_data)
    return redirect(url_for('login'))

# ------------------- STUDENT LOGOUT -------------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

# ------------------- STUDENT FORM -------------------
@app.route('/student_form', methods=['GET', 'POST'])
def student_form():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        data = (
            request.form['name'],
            request.form['email'],
            request.form['phone'],
            request.form['math10'],
            request.form['science10'],
            request.form['english10'],
            request.form['hindi10'],
            request.form['physics12'],
            request.form['chemistry12'],
            request.form['math12'],
            request.form['branch1'],
            request.form['branch2']
        )

        conn = sqlite3.connect('students.db')
        c = conn.cursor()
        c.execute('''INSERT INTO students
            (name, email, phone, math10, science10, english10, hindi10,
            physics12, chemistry12, math12, branch1, branch2)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)

        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))

    return render_template('student_form.html')

# ------------------- ADMIN LOGIN -------------------
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email in admin_credentials and admin_credentials[email] == password:
            session['admin'] = email
            return redirect(url_for('admin_dashboard'))
        else:
            return "Invalid admin credentials"

    return render_template('admin_login.html')

# ------------------- ADMIN DASHBOARD -------------------
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    # Exclude "MANVENDRA SINGH" from the display, ignore case and spaces
    c.execute('''SELECT *, 
        (CAST(physics12 AS INTEGER) + CAST(chemistry12 AS INTEGER) + CAST(math12 AS INTEGER)) AS total_marks
        FROM students
        WHERE UPPER(TRIM(name)) != 'MANVENDRA SINGH'
        ORDER BY total_marks DESC''')
    students = c.fetchall()
    conn.close()
    return render_template('admin_dashboard.html', students=students)

# ------------------- ALLOT BRANCH ROUTE -------------------
@app.route('/allot_branch', methods=['POST'])
def allot_branch():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    email = request.form['email']
    allotted_branch = request.form['allotted_branch']

    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute("UPDATE students SET allotted_branch = ? WHERE email = ?", (allotted_branch, email))
    conn.commit()
    conn.close()

    return redirect(url_for('admin_dashboard'))

# ------------------- CONFIRM SEAT + UPLOAD RECEIPT -------------------
@app.route('/confirm', methods=['GET', 'POST'])
def confirm():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        receipt_file = request.files['receipt']
        if receipt_file:
            filename = secure_filename(receipt_file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            receipt_file.save(filepath)

            conn = sqlite3.connect('students.db')
            c = conn.cursor()
            c.execute("UPDATE students SET confirmed = ?, receipt_filename = ? WHERE name = ?", 
                      ('Yes', filename, session['user']))
            conn.commit()
            conn.close()

            return redirect(url_for('dashboard'))

    return render_template('confirm.html')

# ------------------- ADMIN VERIFIES RECEIPT -------------------
@app.route('/verify_receipt/<email>')
def verify_receipt(email):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute("UPDATE students SET verified = ? WHERE email = ?", ('Yes', email))
    conn.commit()
    conn.close()

    return redirect(url_for('admin_dashboard'))

# ------------------- SERVE RECEIPT FILE -------------------
@app.route('/receipts/<filename>')
def uploaded_receipt(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ------------------- OFFER LETTER GENERATION -------------------
@app.route('/offer_letter')
def offer_letter():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM students WHERE name = ?", (session['user'],))
    student = c.fetchone()
    conn.close()

    if student and student['verified'] == 'Yes':
        return render_template('offer_letter.html', student=student)
    else:
        return "Your offer letter is not yet available."

# ------------------- RUN THE APP -------------------
if __name__ == '__main__':
    app.run(debug=True)
