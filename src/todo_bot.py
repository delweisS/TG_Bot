"""
This module provides a Telegram bot for managing tasks.

To use the bot, first run main.py. Then, use the commands /start, /show, /add, and /delete
to manage your tasks.
"""

import os
import sqlite3

import telebot

from src.database import Database
from src.decorators import authenticated

bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

db = Database(create_table=not os.path.isfile('todo.db'))


# '/start' command handler
@authenticated
@bot.message_handler(commands=['start'])
def handle_start(message):
    """
    Send welcome message.

    Args:
        message: message from user.
    """
    chat_id = message.chat.id
    message = """
Hi 🙃.

I'm a bot to help you keep track of tasks.
You can add delete and view your tasks,
and I'll remember them for you.

If you have any questions, type /help.
    """

    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2)
    keyboard.add(
        telebot.types.KeyboardButton('Add task'),
        telebot.types.KeyboardButton('Delete task'),
    )
    keyboard.add(telebot.types.KeyboardButton('List of tasks'))
    bot.send_message(chat_id, message, reply_markup=keyboard)


# '/help' command handler
@authenticated
@bot.message_handler(commands=['help'])
def handle_help(message):
    """
    Send help message.

    Args:
        message: message from user.
    """
    chat_id = message.chat.id
    message = """
Commands used in the bot:

- /show - shows the full list of tasks
- /add - add new task
- /delete - deletes a task by its number
- /help - FAQ on commands
    """

    bot.send_message(chat_id, message)


# '/show' command/text handler
def handle_show(message):
    """
    Show the list of tasks.

    Args:
        message: message from user.
    """
    chat_id = message.chat.id
    conn = sqlite3.connect(db.db_name)
    tasks = db.get_tasks(conn, chat_id)
    conn.close()
    bot.send_message(chat_id, tasks)


@authenticated
@bot.message_handler(commands=['show'])
def handle_show_command(message):
    """
    Handle /show command.

    Args:
        message: message from user.
    """
    handle_show(message)


@authenticated
@bot.message_handler(func=lambda message: message.text == 'List of tasks')
def handle_show_text(message):
    """
    Handle text 'List of tasks'.

    Args:
        message: message from user.
    """
    handle_show(message)


# '/add' command handler
def handle_add(message):
    """
    Add new task.

    Args:
        message: message from user.
    """
    bot.reply_to(message, 'Enter the name of the task:')
    bot.register_next_step_handler(message, add_task)


@authenticated
@bot.message_handler(commands=['add'])
def handle_add_command(message):
    """
    Handle /add command.

    Args:
        message: message from user.
    """
    handle_add(message)


@authenticated
@bot.message_handler(func=lambda message: message.text == 'Add task')
def handle_add_text(message):
    """
    Handle text 'Add task'.

    Args:
        message: message from user.
    """
    handle_add(message)


def add_task(message):
    """
    Add name to task.

    Args:
        message: message from user.
    """
    chat_id = message.chat.id
    task_name = message.text.strip()

    if not task_name:
        bot.send_message(chat_id, 'The name of the task cannot be empty.')
        return

    bot.reply_to(message, 'Enter a task description (optional):')
    bot.register_next_step_handler(message, add_task_description, chat_id, task_name)


def add_task_description(message, chat_id, task_name):
    """
    Add description to task (optional).

    Args:
        message: message from user.
        chat_id: id of the chat.
        task_name: name of task.
    """
    chat_id = message.chat.id
    task_description = message.text.strip()

    conn = sqlite3.connect(db.db_name)

    if db.add_task(conn, chat_id, task_name, task_description):
        conn.close()
        bot.send_message(chat_id, 'Task "{0}" has been successfully added.'.format(task_name))
    else:
        conn.close()
        bot.send_message(chat_id, 'The task "{0}" already exists.'.format(task_name))


# '/delete' command/text handler
def handle_delete(message):
    """
    Invitation to enter the task id

    Args:
        message: message from user.
    """
    chat_id = message.chat.id
    bot.reply_to(message, 'Enter the id of the task you want to delete:')
    bot.register_next_step_handler(message, delete_task_id, chat_id)


@authenticated
@bot.message_handler(commands=['delete'])
def handle_delete_command(message):
    """
    Handle /delete command.

    Args:
        message: message from user.
    """
    handle_delete(message)


@authenticated
@bot.message_handler(func=lambda message: message.text == 'Delete task')
def handle_delete_text(message):
    """
    Handle text 'Delete task'.

    Args:
        message: message from user.
    """
    handle_delete(message)


# Delete task function
def delete_task_id(message, chat_id):
    """
    Delete task by id.

    Args:
        message: message from user.
        chat_id: id of the chat.
    """
    task_id = message.text.strip()

    if not task_id.isdigit():
        bot.send_message(chat_id, 'Incorrect task identifier. Try again.')
        return

    conn = sqlite3.connect(db.db_name)

    if db.delete_task(conn, task_id, chat_id):
        conn.close()
        bot.send_message(chat_id, 'Task has been successfully deleted.')
    else:
        conn.close()
        bot.send_message(chat_id, 'Task not found.')
