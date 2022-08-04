import os
import json
from configparser import ConfigParser
from rdflib import Graph, Namespace
from rdflib.namespace import NamespaceManager
from rdflib.namespace._RDF import RDF as rdf

config = ConfigParser()
config.read("doaj_bulk.conf")

context_file = config.get("rdf", "context", fallback="context.json")

global JobNamespace
JobNamespace = NamespaceManager(Graph())

with open(context_file, "r") as c:
    doaj_context = json.load(c)

JOB = Namespace(doaj_context.get("job"))
JobNamespace.bind("job", JOB)

SCHEMA = Namespace(doaj_context.get("schema"))
JobNamespace.bind("schema", SCHEMA)

XSD = Namespace(doaj_context.get("xsd"))
JobNamespace.bind("xsd", XSD)

DOAJ = Namespace(doaj_context.get("doaj"))
JobNamespace.bind("doaj", DOAJ)

ISSN = Namespace("https://issn.org/")
JobNamespace.bind("issn", ISSN)

LOCAL = Namespace(f"file://{os.getcwd()}/")
JobNamespace.bind("local", LOCAL)

CC0 = Namespace("https://creativecommons.org/publicdomain/zero/")
JobNamespace.bind("cc0", CC0)

CC = Namespace("https://creativecommons.org/licenses/")
JobNamespace.bind("cc", CC)

global RDF
RDF = rdf
