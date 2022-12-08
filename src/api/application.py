from flask import Flask, make_response, request
from configparser import ConfigParser
from flask.json import jsonify

from marshmallow import ValidationError
from utils.utils import ROOT_DIR
from flasgger import Swagger

api = Flask(__name__)
doc = Swagger(api)
config = ConfigParser()
config.read(f"{ROOT_DIR}/config/api.conf")
api.config.update(dict(config["main"]))

from api.pad import PADView, PADSubView
api.add_url_rule("/pad/<id>", view_func=PADView.as_view("pad_id"))
api.add_url_rule("/pad/<id>/<sub>", view_func=PADSubView.as_view("pad_sub"))

from api.pads import PADsView, PADsIdView
api.add_url_rule("/api/pads", view_func=PADsView.as_view("pads"))
api.add_url_rule("/api/pads/<id>", view_func=PADsIdView.as_view("pads_id"))


@api.errorhandler(400)
@api.errorhandler(401)
@api.errorhandler(404)
@api.errorhandler(500)
@api.errorhandler(ValidationError)
def validationerrorhandler(e):
    if request.args.get("format", "") in ("ttl", "trig", "html"):
        return f"<pre>{str(e.description)}</pre>"
    if request.headers.get("Accept", "") in ("text/html"):
        return f"<pre>{str(e.description)}</pre>"
    return jsonify({"message": str(e.description)}), 400
