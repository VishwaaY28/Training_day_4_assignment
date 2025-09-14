import os

class Config:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@localhost/hospital"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY","my_secret_key")