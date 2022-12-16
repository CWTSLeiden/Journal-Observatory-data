from configparser import ConfigParser
from flasgger import Swagger
from flask import Flask, request
from flask.json import jsonify
from marshmallow import ValidationError
from utils.utils import ROOT_DIR

# Construct and configure the Flask application
api = Flask(__name__)
config = ConfigParser()
config.read(f"{ROOT_DIR}/config/api.conf")
api.config.update(dict(config["main"]))

# Construct and configure the Swagger documentation
doc_config = {
    "info": {
        "title": "Journal Observatory - Platform Assertion Document API",
        "description": (
            "This REST endpoint provides an alternative endpoint to the "
            "Journal Observatory Platform Assertion Document "
            "[SPARQL endpoint](http://localhost:7200/repositories/job)."
        ),
        "version": "0.0.1"
    }
}
doc = Swagger(api, template=doc_config)

# PAD api endpoint
from api.pad import PADView, PADSubView
api.add_url_rule("/pad/<id>", view_func=PADView.as_view("pad_id"))
api.add_url_rule("/pad/<id>/<sub>", view_func=PADSubView.as_view("pad_sub"))

# PADs api endpoint
from api.pads import PADsView, PADsIdView
api.add_url_rule("/api/pads", view_func=PADsView.as_view("pads"))
api.add_url_rule("/api/pads/<id>", view_func=PADsIdView.as_view("pads_id"))

# Error handling
@api.errorhandler(400)
@api.errorhandler(401)
@api.errorhandler(404)
@api.errorhandler(500)
def httperrorhandler(e):
    if request.args.get("format", "") in ("ttl", "trig", "html"):
        return f"<pre>{str(e.description)}</pre>"
    if request.headers.get("Accept", "") in ("text/html"):
        return f"<pre>{str(e.description)}</pre>"
    return jsonify({"message": str(e.description)})

@api.errorhandler(ValidationError)
def validationerrorhandler(e):
    if request.args.get("format", "") in ("ttl", "trig", "html"):
        return f"<pre>{str(e)}</pre>"
    if request.headers.get("Accept", "") in ("text/html"):
        return f"<pre>{str(e)}</pre>"
    return jsonify({"message": str(e)}), 400
