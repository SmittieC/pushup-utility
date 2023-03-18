import sqlite3
from typing import List, Tuple


def database_connection():
    conn = sqlite3.connect('pushups.db')
    return conn.cursor(), conn


def get_user(user_id):
    cursor, conn = database_connection()
    try:
        res, = cursor.execute('SELECT id, username FROM users WHERE id=?', (user_id,))
    except Exception:
        return None
    return res

def get_user_pushup_count(user_id):
    cursor, conn = database_connection()
    cursor.execute('SELECT sum(count) FROM pushups WHERE user_id=? ORDER BY date DESC', (user_id,))
    pushup_count, = cursor.fetchall()[0]
    return pushup_count

def get_count_per_day(user_id) -> List[Tuple[int, str]]:
    cursor, conn = database_connection()
    cursor.execute('select sum(count), date from pushups where user_id=? GROUP BY date ORDER BY date DESC', (user_id,))
    return cursor.fetchall()