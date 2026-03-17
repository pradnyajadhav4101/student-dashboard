from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
from reportlab.platypus import SimpleDocTemplate, Table

app = Flask(__name__)
app.secret_key = "secret"


# -----------GRADE LOGIC--------------------

def calculate_grade(p):
    if p >= 90:
        return "A"
    elif p >= 75:
        return "B"
    elif p >= 50:
        return "C"
    else:
        return "Fail"


# --------------HOME -> LOGIN-----------------

@app.route('/')
def home():
    return redirect('/login')


# -------------REGISTER------------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('register.html')


# -------------LOGIN------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cur.fetchone()
        conn.close()

        if user:
            session['user'] = username
            return redirect('/dashboard')

    return render_template('login.html')


# -----------DASHBOARD--------------------

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    # Add Student
    if request.method == 'POST':
        name = request.form['name']
        sub1 = int(request.form['sub1'])
        sub2 = int(request.form['sub2'])
        sub3 = int(request.form['sub3'])

        percentage = round((sub1 + sub2 + sub3) / 3, 2)
        grade = calculate_grade(percentage)

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO students (name, sub1, sub2, sub3, percentage, grade)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, sub1, sub2, sub3, percentage, grade))
        conn.commit()
        conn.close()

        return redirect('/dashboard')

    # Fetch Data
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM students")
    data = cur.fetchall()
    conn.close()

    # Chart Data
    names = [row[1] for row in data]
    marks = [row[5] for row in data]

    return render_template('dashboard.html', data=data, names=names, marks=marks)


# -------------DELETE------------------

@app.route('/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/dashboard')


# ---------------EDIT----------------

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        sub1 = int(request.form['sub1'])
        sub2 = int(request.form['sub2'])
        sub3 = int(request.form['sub3'])

        percentage = (sub1 + sub2 + sub3) / 3
        grade = calculate_grade(percentage)

        cur.execute('''
            UPDATE students
            SET name=?, sub1=?, sub2=?, sub3=?, percentage=?, grade=?
            WHERE id=?
        ''', (name, sub1, sub2, sub3, percentage, grade, id))

        conn.commit()
        conn.close()

        return redirect('/dashboard')

    cur.execute("SELECT * FROM students WHERE id=?", (id,))
    student = cur.fetchone()
    conn.close()

    return render_template('edit.html', s=student)


# ------------DOWNLOAD PDF-------------------

@app.route('/download')
def download():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT name, percentage, grade FROM students")
    data = cur.fetchall()
    conn.close()

    file_path = "report.pdf"

    pdf = SimpleDocTemplate(file_path)

    table_data = [["Name", "Percentage", "Grade"]]
    for row in data:
        table_data.append(list(row))

    table = Table(table_data)
    pdf.build([table])

    return send_file(file_path, as_attachment=True)


# --------------LOGOUT-----------------

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')


# -------------404 ERROR------------------

@app.errorhandler(404)
def not_found(e):
    return "Page not found! Check URL", 404


# -------------Run App (ONLY ONCE)------------------

if __name__ == "__main__":
    app.run()