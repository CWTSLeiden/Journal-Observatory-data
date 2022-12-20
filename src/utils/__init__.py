from os import path
from configparser import ConfigParser

try:
    ROOT_DIR = path.realpath(path.join(path.dirname(__file__), "../.."))
except:
    ROOT_DIR = ".."

job_config = ConfigParser()
job_config.read(f"{ROOT_DIR}/config/job.conf")

api_config = ConfigParser()
api_config.read(f"{ROOT_DIR}/config/api.conf")
