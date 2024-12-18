import sqlite3

connection = sqlite3.connect('mydatabase.db')

# Add a new column for transport preference
connection.execute('ALTER TABLE employees ADD COLUMN transport TEXT')

connection.commit()
connection.close()
