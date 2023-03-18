import db_utils

c, conn = db_utils.database_connection()
# Create tables if they don't exist
c.execute('''
          CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
          )
        ''')

c.execute('''
          CREATE TABLE IF NOT EXISTS pushups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            count INTEGER NOT NULL,
            date DATE NOT NULL DEFAULT CURRENT_DATE,
            FOREIGN KEY(user_id) REFERENCES users(id)
          )
        ''')