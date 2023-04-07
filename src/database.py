"""
The Database module provides a class for interacting with an SQLite database.

Example usage:

    db = Database()  # creates a new database called todo.db
    conn = sqlite3.connect('todo.db')
    db.add_task(conn, 1, 'Buy groceries')
    db.get_tasks(conn, 1)  # returns a string of the user's tasks

"""

import sqlite3


class Database(object):
    """
    A class for interacting with an SQLite database that stores tasks.

    Attributes:
        db_name (str): The name of the database file.
    """

    def __init__(self, db_name='todo.db', create_table=True):
        """
        Initialize the Database object.

        Args:
            db_name (str, optional): The name of the database file.
            create_table (bool, optional): Create the 'tasks' table.
        """
        self.db_name = db_name

        if create_table:
            self.setup()

    def setup(self):
        """Create the 'tasks' table in the database if it doesn't exist."""
        with sqlite3.connect(self.db_name) as conn:
            query = """CREATE TABLE IF NOT EXISTS tasks
                                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    chat_id INTEGER NOT NULL,
                                    name TEXT NOT NULL,
                                    description TEXT,
                                    UNIQUE(chat_id, name))"""
            conn.execute(query)
            conn.commit()

    def add_task(
        self,
        conn,
        chat_id: int,
        task_name: str,
        description: str = None,
    ) -> int:
        """
        Add a task to the database.

        Args:
            conn (sqlite3.Connection): The SQLite database connection.
            chat_id (int): The chat ID of the user who owns the task.
            task_name (str): The name of the task.
            description (str): A description of the task. Defaults to None.

        Returns:
            int: The ID of the newly created task.
        """
        query = """INSERT OR IGNORE INTO tasks
                    (chat_id, name, description)
                    VALUES (?, ?, ?)"""
        cursor = conn.cursor()
        cursor.execute(query, (chat_id, task_name, description))
        conn.commit()

        return cursor.lastrowid

    def delete_task(self, conn, chat_id: int, task_id: int) -> bool:
        """
        Delete a task from the database.

        Args:
            conn (sqlite3.Connection): The SQLite database connection.
            chat_id (int): The chat ID of the user who owns the task.
            task_id (int): The ID of the task to delete.

        Returns:
            bool: True if a task was deleted, False otherwise.
        """
        query = 'DELETE FROM tasks WHERE id=? AND chat_id=?'
        cursor = conn.cursor()
        cursor.execute(query, (task_id, chat_id))
        conn.commit()

        return cursor.rowcount > 0

    def get_tasks(self, conn, chat_id: int) -> str:
        """
        Get a user's tasks from the database and returns them as a string.

        Args:
            conn (sqlite3.Connection): The SQLite database connection.
            chat_id (int): The chat ID of the user whose tasks to retrieve.

        Returns:
            str: A string containing the user's tasks, formatted as a numbered list.
        """
        query = 'SELECT name, id FROM tasks WHERE chat_id = ?'
        cursor = conn.cursor()
        tasks = cursor.execute(query, (chat_id,)).fetchall()

        message = 'Your task list:\n\n'

        if tasks:
            tasks_list = ['{0}) {1}\n'.format(task[1], task[0]) for task in tasks]
            message = message + ''.join(tasks_list)
        else:
            message = 'The task list is empty.'

        return message
