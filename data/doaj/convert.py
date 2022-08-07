from configparser import ConfigParser
from os import path
import shutil
import re
from rdflib import Graph
from namespace import JobNamespace


config = ConfigParser()
config.read("doaj_bulk.conf")
store = config.get("rdf", "store", fallback="store.db")
raw_store = config.get("rdf", "raw_store", fallback="raw_store.db")


def init_store(store_path, id, clear=False):
    if clear and path.exists(store_path):
        shutil.rmtree(store_path)
    graph = Graph(store="BerkeleyDB", namespace_manager=JobNamespace, identifier=id)
    graph.open(store_path, create=clear)
    return graph
    

def query():
    # job_graph = init_store(store, id="job", clear=True)
    # doaj_graph = init_store(raw_store, id="doaj", clear=False)
    job_graph = Graph(namespace_manager=JobNamespace)
    doaj_graph = Graph(namespace_manager=JobNamespace)
    doaj_graph.parse("apc.ttl")
    with open("convert.sparql", "r") as sparql_query:
        query = sparql_query.read().split("\n")
    query = ["" if re.search("^ *#", q) else q for q in query]
    query = " ".join(query)
    job_graph += doaj_graph.query(query)
    job_graph.serialize("jobmap.ttl", format="turtle")

    job_graph.close()
    doaj_graph.close()
        
    
query()
