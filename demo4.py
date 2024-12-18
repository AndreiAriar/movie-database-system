import sqlite3

connection = sqlite3.connect('mydatabase.db')

connection.execute('''
    CREATE TABLE IF NOT EXISTS employees(
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                name TEXT,
                age TEXT,
                favorite_movie TEXT 
                )
                ''')

# Insert data
employee_data = [
    ('John Smith', '30', 'The Shawshank Redemption'),
    ('Maria Gonzalez', '45', 'Forrest Gump'),
    ('David Chen', '28', 'The Dark Knight'),
    ('Lisa Carter', '35', 'The Godfather'),
    ('Ahmed Khan', '40', 'Pulp Fiction'),
]

connection.executemany('''
    INSERT INTO employees (name, age, favorite_movie) VALUES (?, ?, ?)
    ''', employee_data)

# Query data from the table
result = connection.execute('SELECT * FROM employees ORDER BY age DESC')
data = result.fetchall()

# Display data
for row in data:
    print(f'Name: {row[1]}')
    print(f'Age: {row[2]}')
    print(f'Favorite Movie: {row[3]}')
    print('')

connection.commit()
connection.close()
