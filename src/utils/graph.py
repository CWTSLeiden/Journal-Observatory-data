from os import path
import shutil
from rdflib import ConjunctiveGraph, Graph
from namespace import JobNamespace
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore, SPARQLStore
from rdflib import BNode


def bnode_to_sparql(node):
    if isinstance(node, BNode):
        return f"<bnode:b{node}>"
    return node.n3()


def sparql_insert_graph(graph : Graph, add_graph : Graph):
    "A more efficient alternative to Graph.__add__"
    graph.update(f"insert data {{ {add_graph.serialize(format='nt')} }}")


def job_graph(id=None, nm=None, store="default"):
    if not nm:
        nm = JobNamespace()
    graph = ConjunctiveGraph(store=store, identifier=id)
    graph.namespace_manager = nm
    return graph


def fuseki_graph(type="read", endpoint="http://localhost:3030/job", id=None, clear=False, nm=None):
    if not nm:
        nm = JobNamespace()
    if type == "write":
        db = SPARQLUpdateStore(
            node_to_sparql=bnode_to_sparql,
            query_endpoint=f"{endpoint}/query",
            update_endpoint=f"{endpoint}/update",
            auth=('admin','test')
        )
        graph = Graph(store=db, identifier=id)
    else:
        db = SPARQLStore(
            node_to_sparql=bnode_to_sparql,
            query_endpoint=f"{endpoint}/query",
            auth=('admin','test')
        )
        graph = ConjunctiveGraph(store=db, identifier=id)
    if clear:
        n = graph.__len__()
        if n:
            print(f"clear graph {graph.identifier} with {n} triples...", end=" ")
            graph.update(f"clear graph <{graph.identifier}>")
            print("done")
    graph.namespace_manager = nm
    return graph
