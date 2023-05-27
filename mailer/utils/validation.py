import re

def is_valid_email(email):
    # Code to validate email format
    # ...
    return re.match(r'^[\w.-]+@[\w.-]+\.\w+$', email) is not None
