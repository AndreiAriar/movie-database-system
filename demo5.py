import sqlite3

connection = sqlite3.connect('mydatabase.db')

connection.execute('''
    CREATE TABLE IF NOT EXISTS students(
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    name TEXT,
                    age INTEGER
                )
                ''')

connection.execute('''
    CREATE TABLE IF NOT EXISTS movies(
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    title TEXT,
                    student_id INTEGER,
                    FOREIGN KEY (student_id) REFERENCES students(id)
                )
                ''')

students_data = [
    ('John Doe', 20),
    ('Jane Smith', 22),
    ('Mike Johnson', 21),
    ('Emily Brown', 19),
    ('David Lee', 23),
]

movies_data = [
    ('The Shawshank Redemption', 1),
    ('The Godfather', 2),
    ('The Dark Knight', 3),
    ('Forrest Gump', 4),
    ('Pulp Fiction', 5),
]

connection.executemany('''
    INSERT INTO students (name, age) VALUES (?, ?)
    ''', students_data)
connection.executemany('''
    INSERT INTO movies (title, student_id) VALUES (?, ?)
    ''', movies_data)

results = connection.execute('''
    SELECT students.name, movies.title
    FROM students
    INNER JOIN movies ON students.id = movies.student_id
    ''')

connection.commit()

print('Students - Movie Relationship')
for row in results.fetchall():
    print(f'Student: {row[0]}')
    print(f'Movie: {row[1]}')
    print('')

connection.close()
