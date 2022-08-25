from sys import stdout
from os import path
import shutil
from rdflib import Graph
from namespace import JobNamespace
from rdflib.plugins.stores import sparqlstore
from rdflib import BNode

try:
    ROOT_DIR = path.realpath(path.join(path.dirname(__file__), ".."))
except:
    ROOT_DIR = ".."

class Progress():
    def __init__(self, total, text="Progress: ", verbose=True):
        self.total = total
        self.perc = 0
        self.text = text
        self.verbose = verbose
        
    def print_progress(self, n):
        if self.verbose:
            p = int(((n / self.total) * 100))
            if self.perc != p and self.perc < 100:
                self.perc = p
                stdout.write(f"\r{self.text}{self.perc : >3}%")
                stdout.flush()
                if self.perc == 100:
                    print("")


def bnode_to_sparql(node):
   if isinstance(node, BNode):
       return f"<bnode:b{node}>"
   return sparqlstore._node_to_sparql(node)


def init_graph(db_type="", id=None, db_path=None, clear=True, nm=None):
    if not nm:
        nm = JobNamespace()
    if db_type in ["BerkeleyDB"] and db_path:
        db = path.join(db_path, f"{id}.berkeleydb")
        if clear and path.exists(db):
            shutil.rmtree(db)
        graph = Graph(store=db_type, namespace_manager=nm, identifier=id)
        graph.open(db, create=clear)
        return graph
    elif db_type in ["fuseki"]:
        db = sparqlstore.SPARQLUpdateStore(
            query_endpoint=f"{db_path}/query",
            update_endpoint=f"{db_path}/update",
            node_to_sparql=bnode_to_sparql,
            auth=('admin','test')
        )
        graph = Graph(store=db, namespace_manager=nm, identifier=id)
        return graph
    elif db_type in ["blazegraph"]:
        db = sparqlstore.SPARQLUpdateStore(
            query_endpoint=db_path,
            update_endpoint=db_path,
            node_to_sparql=bnode_to_sparql
        )
        graph = Graph(store=db, namespace_manager=nm, identifier=id)
        return graph
    return Graph(namespace_manager=nm, identifier=id)


def print_graph(graph, max=10):
    print("-" * 80)
    for n, (s, p, o) in enumerate(graph):
        if n > max: break
        print(f"sub: {s}")
        print(f"rel: {p}")
        print(f"obj: {o}")
        print("-" * 80)


def ext_to_format(ext):
    formats = {
        "ttl": "ttl",
        "jsonld": "json-ld"
    }
    return formats.get(ext) or ext


def print_this(graph, pre=""):
    for n, uri in graph.namespaces():
        if n == "this":
            print(f"{pre}{uri}")
            return uri
    print(f"{pre}not found")


def add_to_graph(graph, subgraph):
    for s, p, o in subgraph:
        graph.add((s, p, o))
    return graph

