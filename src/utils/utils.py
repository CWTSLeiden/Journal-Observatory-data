import json
from os import path

try:
    ROOT_DIR = path.realpath(path.join(path.dirname(__file__), "../.."))
except:
    ROOT_DIR = ".."


def ext_to_format(ext):
    formats = {
        "ttl": "ttl",
        "jsonld": "json-ld"
    }
    return formats.get(ext) or ext


def file_to_json(file):
    with open(file, "rb") as f:
        return json.load(f)
