from flask import Flask
from logger import setup_logger
from routes.mail_routes import mail_blueprint
from dotenv import load_dotenv

load_dotenv(".env")

app = Flask(__name__)
setup_logger(app)

app.register_blueprint(mail_blueprint)


if __name__ == '__main__':
    app.run(port="5003")