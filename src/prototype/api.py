from flask import Flask
from prototype.display_pad import test


api = Flask(__name__)

@api.route("/")
@api.route("/<n>")
def pad(n=0):
    return test(n)
