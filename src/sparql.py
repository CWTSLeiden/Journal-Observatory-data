import json
from SPARQLWrapper import SPARQLWrapper, JSONLD, JSON

with open("../data/issn_qss.json") as f:
    issn_qss_json = json.load(f)
    
