from configparser import ConfigParser
from rdflib import BNode
from rdflib import ConjunctiveGraph, Dataset
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore, SPARQLStore
from utils.graph import pad_graph
from utils.namespace import PAD, PPO, PADNamespaceManager
from utils.print import print_verbose
from utils.utils import ROOT_DIR
import requests


def bnode_to_sparql(node):
    if isinstance(node, BNode):
        return f"<bnode:b{node}>"
    return node.n3()


def sparql_store(update=False, nm=None):
    config = ConfigParser()
    config.read(f"{ROOT_DIR}/config/job.conf")
    query_endpoint = config.get("store", "query")
    update_endpoint = config.get("store", "update")
    if update:
        username = config.get("store", "username")
        password = config.get("store", "password")
        db = SPARQLUpdateStore(
            node_to_sparql=bnode_to_sparql,
            query_endpoint=query_endpoint,
            update_endpoint=update_endpoint,
            auth=(username, password)
        )
    else:
        db = SPARQLStore(
            node_to_sparql=bnode_to_sparql,
            query_endpoint=query_endpoint
        )
    graph = Dataset(store=db)
    graph.namespace_manager = (nm or PADNamespaceManager())
    return graph


def clear_default_graph(graph, confirm=False):
    n = graph.__len__()
    if n:
        if not confirm:
            r = input(f"Clear graph {graph.identifier} with {n} triples? y/[n]")
            confirm = r in ("y", "Y", "yes", "Yes")
        if confirm:
            print_verbose(f"Clear graph {graph.identifier}...", end="")
            graph.update(f"drop all")
            print_verbose("done")
    else:
        print_verbose(f"Graph {graph.identifier} has no triples.")


def clear_pads(graph, pads=[]):
    update = ""
    for pad in pads:
        update = f"drop graph <{pad}/provenance>; "
        update += f"drop graph <{pad}/assertion>; "
        update += f"drop graph <{pad}/docinfo>; "
    graph.update(update)


def clear_by_creator(graph, creators):
    query = f"""
    SELECT ?pad
    WHERE {{
        graph ?docinfo {{ ?pad pad:hasProvenance ?provenance . }}
        graph ?provenance {{ ?assertion dcterms:creator ?creator . }}
        filter (?creator in {", ".join(creators)})
    }}
    """
    result = graph.query(query)
    pads = [p.pad for p in result]
    print(f"clear {len(pads)} PADs")
    clear_pads(graph, pads)


def add_ontology(graph : ConjunctiveGraph):
    print_verbose("Add ontology")
    ppo_id = PPO.ontology
    pad_id = PAD.ontology
    batchgraph = pad_graph()
    batchgraph.parse(source=f"{ROOT_DIR}/ontology/ppo_ontology.ttl", publicID=ppo_id)
    batchgraph.parse(source=f"{ROOT_DIR}/ontology/pad_framework.ttl", publicID=pad_id)
    graph.update(f"clear graph <{ppo_id}>")
    graph.update(f"clear graph <{pad_id}>")
    graph.addN(batchgraph.quads())


def graphdb_add_namespaces(query_endpoint):
    if "/repositories/" in query_endpoint:
        print_verbose("Add namespaces to GraphDB")
        for prefix, uri in dict(PADNamespaceManager().namespaces()).items():
            if prefix not in ("this", "sub"):
                url = f"{query_endpoint}/namespaces/{prefix}"
                requests.put(url, data=uri)
    else:
        print_verbose("Endpoint is not a GraphDB instance, no namespaces added.")
