#!/usr/bin/env python

"""
This module starts the Todo Bot application by calling the `infinity_polling`.

Example usage:

    $ python main.py

"""

from src.todo_bot import bot

if __name__ == '__main__':
    bot.infinity_polling()
