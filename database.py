import sqlite3

conn = sqlite3.connect('database.db')
cur = conn.cursor()

# Users table
cur.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
''')

# Students table (multiple subjects)
cur.execute('''
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    sub1 INTEGER,
    sub2 INTEGER,
    sub3 INTEGER,
    percentage REAL,
    grade TEXT
)
''')

conn.commit()
conn.close()

print("Database ready!")