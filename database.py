import sqlite3

conn = sqlite3.connect('students.db')
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        phone TEXT,
        math10 INTEGER,
        science10 INTEGER,
        english10 INTEGER,
        hindi10 INTEGER,
        physics12 INTEGER,
        chemistry12 INTEGER,
        math12 INTEGER,
        branch1 TEXT,
        branch2 TEXT,
        allotted_branch TEXT,
        confirmed TEXT,
        receipt_filename TEXT,
        verified TEXT
    )
''')

conn.commit()
conn.close()
print("✅ Table created/updated successfully.")

