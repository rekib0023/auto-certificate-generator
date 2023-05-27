from dotenv import load_dotenv
load_dotenv(".env")


# Flask-Mail Configuration
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = 'your_email@gmail.com'
MAIL_PASSWORD = 'your_password'
DEBUG=True