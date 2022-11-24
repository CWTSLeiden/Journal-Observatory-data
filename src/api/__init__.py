from flask import Flask

api = Flask(__name__)

from api import routes
