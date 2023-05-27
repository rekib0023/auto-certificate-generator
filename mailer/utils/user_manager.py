from mailer.email_service.sender import send_email
from email_service.templates.email_templates import generate_welcome_email_template, generate_password_reset_template
from utils.validation import is_valid_email

def register_user(email, username, password):
    if not is_valid_email(email):
        return False
    
    welcome_email = generate_welcome_email_template(username)
    send_email(email, "Welcome to our platform", welcome_email)
    
    return True

def reset_password(email):
    if not is_valid_email(email):
        return False
    
    password_reset_email = generate_password_reset_template(email)
    send_email(email, "Password Reset", password_reset_email)
    
    return True
