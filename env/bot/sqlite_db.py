from os import curdir
import sqlite3 as sq

async def db_connect():
    global db, cur

    db = sq.connect('todos.db')
    cur = db.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS todo(id INTEGER PRIMARY KEY AUTOINCREMENT, description varchar(500) NOT NULL, planned_date datetime, dt datetime default current_timestamp, is_done BOOLEAN DEFAULT FALSE)")

    db.commit()

async def get_all_todos():
    return  cur.execute('SELECT * FROM todo').fetchall()

async def create_todo(state):
    async with state.proxy() as data:
        todo = cur.execute("INSERT INTO todo (description, planned_date) VALUES(?, ?)", (data['desc'], data['planned_date']))
        db.commit()

    return todo

async def delete_todo(todo_id):
    cur.execute('DELETE FROM todo where id = ?', (todo_id,))
    db.commit()

async def update_todo(todo_id):
    cur.execute('UPDATE todo SET is_done = TRUE where id = ?', (todo_id,))
    db.commit()