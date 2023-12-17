from flask import Flask
from flask_wtf import Form
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

from app import routes

if __name__ == "__main__":
    app.run()