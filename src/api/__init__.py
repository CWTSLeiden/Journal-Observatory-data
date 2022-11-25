from flask import Flask
from configparser import ConfigParser
from utils.utils import ROOT_DIR

api = Flask(__name__)
config = ConfigParser()
config.read(f"{ROOT_DIR}/config/api.conf")
api.config.update(dict(config["main"]))

from api import routes
