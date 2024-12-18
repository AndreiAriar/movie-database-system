import sqlite3

connection = sqlite3.connect('mydatabase.db')

connection.execute('''
    CREATE TABLE IF NOT EXISTS movies(
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                title TEXT,
                director TEXT,
                year INTEGER 
                )
                ''')

movies_data = [
    ('The Shawshank Redemption', 'Frank Darabont', 1994),
    ('The Godfather', 'Francis Ford Coppola', 1972),
    ('The Dark Knight', 'Christopher Nolan', 2008),
    ('Pulp Fiction', 'Quentin Tarantino', 1994),
    ('Forrest Gump', 'Robert Zemeckis', 1994),
]

connection.executemany('''
    INSERT INTO movies (title, director, year) VALUES (?, ?, ?)
    ''', movies_data)

# Query data from the table
result = connection.execute('SELECT * FROM movies')
data = result.fetchall()

# Display data
for row in data:
    print(f'Title: {row[1]}')
    print(f'Director: {row[2]}')
    print(f'Year: {row[3]}')
    print('')

connection.commit()
connection.close()
