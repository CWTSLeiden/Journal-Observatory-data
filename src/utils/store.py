from configparser import ConfigParser
import os
from rdflib import BNode
from rdflib import ConjunctiveGraph, Dataset
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore, SPARQLStore
from utils.namespace import PAD, PPO, PADNamespaceManager
from utils.pad import PADGraph
from utils.print import print_verbose
from utils import pad_config as config


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
    for n, pad in enumerate(pads):
        update += f"clear graph <{pad}/provenance>; "
        update += f"clear graph <{pad}/assertion>; "
        update += f"clear graph <{pad}/docinfo>; "
    graph.update(update)


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
    print_verbose(f"clear {len(pads)} PADs")
    clear_pads(graph, pads)


def add_ontology(graph : ConjunctiveGraph):
    batchgraph = PADGraph()
    graph.update(f"clear graph <{PPO.ontology}>")
    batchgraph.parse(
        source=config.getpath("store", "ppo_ontology", fallback="ontology/ppo_ontology.ttl"),
        publicID=PPO.ontology
    )
    graph.update(f"clear graph <{PAD.ontology}>")
    batchgraph.parse(
        source=config.getpath("store", "pad_ontology", fallback="ontology/pad_framework.ttl"),
        publicID=PAD.ontology
    )
    batchgraph.parse(
        source=config.getpath("store", "pad_creators", fallback="ontology/pad_creators.ttl"),
        publicID=PAD.ontology
    )
    graph.addN(batchgraph.quads())
