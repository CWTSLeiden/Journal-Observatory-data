from configparser import ConfigParser
from rdflib import ConjunctiveGraph
from namespace import JobNamespace
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore, SPARQLStore
from rdflib import BNode
from utils.utils import ROOT_DIR


def bnode_to_sparql(node):
    if isinstance(node, BNode):
        return f"<bnode:b{node}>"
    return node.n3()


def clear_default_graph(graph):
    n = graph.__len__()
    if n:
        r = input(f"Clear graph {graph.identifier} with {n} triples? y/[n]")
        if r in ("y", "Y", "yes", "Yes"):
            graph.update(f"drop all")
            print("done")
    else:
        print(f"Graph {graph.identifier} has no triples.")


def clear_pads(graph, pads=[]):
    update = ""
    for pad in pads:
        update += f"drop graph <{pad}#head>; "
        update += f"drop graph <{pad}#provenance>; "
        update += f"drop graph <{pad}#assertion>; "
    graph.update(update)


def clear_by_creator(graph, creator):
    query = f"""
    SELECT ?pad
    WHERE {{
        graph ?head {{ ?pad ppo:hasProvenance ?provenance . }}
        graph ?provenance {{ ?assertion dcterms:creator <{creator}> . }}
    }}
    """
    result = graph.query(query)
    pads = [ p.pad for p in result ]
    print(f"clear {len(pads)} PADs")
    clear_pads(graph, pads)


def sparql_store(update=False, id=None, nm=None):
    config = ConfigParser()
    config.read(f"{ROOT_DIR}/config/job.conf")
    endpoint = config.get("store", "endpoint")
    if update:
        username = config.get("store", "username")
        password = config.get("store", "password")
        db = SPARQLUpdateStore(
            node_to_sparql=bnode_to_sparql,
            query_endpoint=f"{endpoint}/query",
            update_endpoint=f"{endpoint}/update",
            auth=(username, password)
        )
    else:
        db = SPARQLStore(
            node_to_sparql=bnode_to_sparql,
            query_endpoint=f"{endpoint}/query"
        )
    graph = ConjunctiveGraph(store=db, identifier=id)
    graph.namespace_manager = (nm or JobNamespace())
    return graph
