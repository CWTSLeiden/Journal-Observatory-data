from flask import Flask
from configparser import ConfigParser
from utils.utils import ROOT_DIR
from flasgger import Swagger
from flask_restful import Api

api = Flask(__name__)
doc = Swagger(api)
config = ConfigParser()
config.read(f"{ROOT_DIR}/config/api.conf")
api.config.update(dict(config["main"]))

restapi = Api(api)

from api.pad import PADResource
restapi.add_resource(PADResource, "/pad/<id>", "/pad/<id>/<sub>")

from api.pads import PADsResource
restapi.add_resource(PADsResource, "/api/pads", endpoint="pads")

