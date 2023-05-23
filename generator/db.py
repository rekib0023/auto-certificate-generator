import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]
DB_DATABASE = os.environ["MYSQL_DATABASE"]
DB_PASSWORD = os.environ["MYSQL_ROOT_PASSWORD"]
DB_USER = os.environ["MYSQL_USER"]

SQLALCHEMY_URI = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}?charset=utf8"

engine = create_engine(SQLALCHEMY_URI)

Session = sessionmaker(bind=engine)


def init_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_URI
    return SQLAlchemy(app)
