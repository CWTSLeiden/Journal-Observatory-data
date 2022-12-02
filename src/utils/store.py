from configparser import ConfigParser
from rdflib import ConjunctiveGraph, Dataset
from utils.namespace import JobNamespace
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore, SPARQLStore
from rdflib import BNode
from utils.utils import ROOT_DIR
from utils.print import print_verbose


def bnode_to_sparql(node):
    if isinstance(node, BNode):
        return f"<bnode:b{node}>"
    return node.n3()


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
        update += f"drop graph <{pad}#head>; "
        update += f"drop graph <{pad}#provenance>; "
        update += f"drop graph <{pad}#assertion>; "
        update += f"drop graph <{pad}#docinfo>; "
    graph.update(update)


def clear_by_creator(graph, creators):
    query = f"""
    SELECT ?pad
    WHERE {{
        graph ?head {{ ?pad ppo:hasProvenance ?provenance . }}
        graph ?provenance {{ ?assertion dcterms:creator ?creator . }}
        filter (?creator in {", ".join(creators)})
    }}
    """
    result = graph.query(query)
    pads = [ p.pad for p in result ]
    print(f"clear {len(pads)} PADs")
    clear_pads(graph, pads)


def sparql_store(update=False, nm=None):
    config = ConfigParser()
    config.read(f"{ROOT_DIR}/config/job.conf")
    query_endpoint = config.get("store", "endpoint")
    update_endpoint = config.get("store", "endpoint")
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
    graph.namespace_manager = (nm or JobNamespace())
    return graph
