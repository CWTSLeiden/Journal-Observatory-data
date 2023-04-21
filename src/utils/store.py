from configparser import ConfigParser
import os
from rdflib import BNode
from rdflib import ConjunctiveGraph, Dataset
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore, SPARQLStore
from urllib.error import HTTPError
from utils.namespace import PAD, SCPO, PADNamespaceManager
from utils.pad import PADGraph
from utils.print import print_verbose
from utils import pad_config as config
from tqdm import tqdm
from functools import partial
from time import sleep


def bnode_to_sparql(node):
    if isinstance(node, BNode):
        return f"<bnode:b{node}>"
    return node.n3()


def sparql_store(query_endpoint : str, update_endpoint : str="", credentials=("", "")) -> Dataset:
    if update_endpoint:
        db = SPARQLUpdateStore(
            node_to_sparql=bnode_to_sparql,
            query_endpoint=query_endpoint,
            update_endpoint=update_endpoint,
            auth=credentials
        )
    else:
        db = SPARQLStore(
            node_to_sparql=bnode_to_sparql,
            query_endpoint=query_endpoint
        )
    graph = Dataset(store=db)
    graph.namespace_manager = PADNamespaceManager()
    return graph


def sparql_store_config(config : ConfigParser, update=False) -> Dataset:
    host = os.getenv("APP_SPARQL_HOST", config.get("store", "host"))
    query_path = os.getenv("APP_SPARQL_QUERY_PATH", config.get("store", "query_path"))
    query_endpoint = f"{host}{query_path}"
    if update:
        update_path = os.getenv("APP_SPARQL_UPDATE_PATH", config.get("store", "update_path"))
        update_endpoint = f"{host}{update_path}"
        username = os.getenv("APP_SPARQL_USERNAME", config.get("store", "username", fallback=""))
        password = os.getenv("APP_SPARQL_PASSWORD", config.get("store", "password", fallback=""))
        return sparql_store(query_endpoint, update_endpoint, (username, password))
    return sparql_store(query_endpoint)


def clear_default_graph(graph, confirm=False):
    n = graph.__len__()
    if n:
        if not confirm:
            r = input(f"Clear graph {graph.identifier} with {n} triples? y/[n]")
            confirm = r in ("y", "Y", "yes", "Yes")
        if confirm:
            print_verbose(f"Clear graph {graph.identifier}")
            graph.update("drop all")
    else:
        print_verbose(f"Graph {graph.identifier} has no triples.")


def clear_pads(graph, pads=[]):
    update = ""
    batchsize = 1000
    batches = [pads[n:n+batchsize] for n in range(0, len(pads), batchsize)]
    progress = partial(tqdm, unit_scale=batchsize, total=len(batches))
    for batch in progress(batches):
        for pad in batch:
            update += f"clear graph <{pad}/provenance>; "
            update += f"clear graph <{pad}/assertion>; "
            update += f"clear graph <{pad}/docinfo>; "
        graph.update(update)
        sleep(5)


def clear_by_creator(graph, creator):
    query = f"""
    SELECT ?pad
    WHERE {{
        graph ?docinfo {{ ?pad pad:hasProvenance ?provenance . }}
        graph ?provenance {{ ?assertion dcterms:creator <{creator}> . }}
    }}
    """
    result = graph.query(query)
    pads = [p.pad for p in result]
    print_verbose(f"clear {len(pads)} PADs for creator: {creator}")
    clear_pads(graph, pads)


def format_from_path(path: str):
    formats = {"ttl": "ttl", "json": "jsonld", "trig": "trig"}
    split = path.split('.')
    if len(split) > 0:
        return formats.get("ttl")
    return formats.get(split[-1], "ttl")
    

def add_ontology(graph : ConjunctiveGraph):
    batchgraph = PADGraph()

    scpo_ontology = config.getpath("store", "scpo_ontology")
    graph.update(f"clear graph <{SCPO.ontology}>")
    batchgraph.parse(
        source=str(scpo_ontology),
        publicID=SCPO.ontology,
        format=format_from_path(str(scpo_ontology))
    )

    pad_ontology = config.getpath("store", "pad_ontology")
    graph.update(f"clear graph <{PAD.ontology}>")
    batchgraph.parse(
        source=str(pad_ontology),
        publicID=PAD.ontology,
        format=format_from_path(str(pad_ontology))
    )

    pad_creators = config.getpath("store", "pad_creators", fallback="ontology/pad_creators.ttl")
    batchgraph.parse(
        source=str(pad_creators),
        publicID=PAD.creators,
        format=format_from_path(str(pad_creators))
    )
    graph.addN(batchgraph.quads())
