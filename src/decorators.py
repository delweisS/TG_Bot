"""
This module provides a decorator for checking if a user is authorized to access.

Example usage:
    from authenticated import authenticated

    @authenticated
    def my_function(message):
"""


import os
from functools import wraps

from dotenv import load_dotenv

load_dotenv()

ALLOWED_USERS = os.getenv('ALLOWED_USERS').split(',')


def authenticated(func):
    """
    Check if a user is authorized to access a function.

    Args:
        func (function): The function to be wrapped.

    Returns:
        function: The wrapper function that checks if the user is authorized.
    """
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        if message.from_user.username not in ALLOWED_USERS:
            return None
        return func(message, *args, **kwargs)
    return wrapper
