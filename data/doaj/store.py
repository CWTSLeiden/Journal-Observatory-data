import json
import sys
from configparser import ConfigParser
import os
import shutil
from glob import glob
from rdflib import Graph, term
from pyld import jsonld
from namespace import JobNamespace as nm
from utils import Progress

config = ConfigParser()
config.read("doaj_bulk.conf")

bulk_import_directory = config.get("import", "dir", fallback="~/")
import_dir = f"{bulk_import_directory}/20220703_doaj"
data_dir = f"{import_dir}/data"
context_file = config.get("rdf", "context", fallback="context.json")
store_file = config.get("rdf", "raw_store", fallback="store.db")

def issn_from_bulk(issn):
    file = f"{data_dir}/{issn}.json"
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    else:
        print("Issn does not exist in files")


def doaj_add_context(record):
    context_record = record.copy()
    with open(context_file, "r") as c:
        context_record["@context"] = json.load(c)
    return context_record


def jsonl_to_rdf(record, graph=Graph()):
    expanded = jsonld.compact(record, record["@context"])
    graph.parse(data=json.dumps(expanded), format='json-ld')
    return graph


def print_graph(graph):
    triples = []
    for t in graph.triples((None, None, None)):
        triples.append(t)
    triples.sort(key=lambda x: x[0])
    print("-" * 50)
    for s, p, o in triples:
        print(f"S: {s}")
        if isinstance(s, term.Literal):
            print(f"    t: {s.datatype}")
        print(f"P: {p}")
        if isinstance(p, term.Literal):
            print(f"    t: {p.datatype}")
        print(f"O: {o}")
        if isinstance(o, term.Literal):
            print(f"    t: {o.datatype}")
        print("-" * 50)

def store(max=(2**32)):
    n = 0
    graph = Graph(store="BerkeleyDB", namespace_manager=nm, identifier="doaj")
    if os.path.exists(store_file):
        shutil.rmtree(store_file)
    graph.open(store_file, create=True)
    files = glob(f"{data_dir}/*.json")
    max = min(max, len(files))
    p = Progress(max)
    for file in files:
        with open(file, "rb") as f:
            journal_json = json.load(f)
        journal_jsonld = doaj_add_context(journal_json)
        jsonl_to_rdf(journal_jsonld, graph)
        n += 1
        if n >= max:
            break
        p.print_progress(n)
    graph.serialize(destination="apc.ttl", format="turtle")
    print(f"Created Graph: {len(graph)} triples")
    graph.close()

store(max=1)
