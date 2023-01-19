from flask import Flask
from prototype.display_pad import *


api = Flask(__name__)

@api.route("/<n>")
def pad(n=0):
    return test(n)
