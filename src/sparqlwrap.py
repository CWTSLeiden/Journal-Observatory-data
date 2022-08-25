from utils import bnode_to_sparql, init_graph
from configparser import ConfigParser
from glob import glob
from utils import ROOT_DIR, init_graph, ext_to_format
from tqdm import tqdm as progress
from store import *
from rdflib.plugins.stores import sparqlstore
from SPARQLWrapper import SPARQLWrapper, POST


config = ConfigParser()
config.read(f"{ROOT_DIR}/config/job.conf")
bulk_dir = config.get("doaj", "bulk_path", fallback="~/")
context_file = config.get("doaj", "context_file", fallback="")
db_max = 10
 
endpoint = SPARQLWrapper("http://localhost:8999/blazegraph/namespace/kb/sparql")
endpoint.setMethod(POST)

files = glob(f"{bulk_dir}/rdf/*.ttl")

for f in progress(files[:100]):
    graph.parse(f)

graph.commit()
graph.close()


# for s in g.query("select ?s where { ?s <https://schema.org/eissn> ?o }"):
#     print(s)
