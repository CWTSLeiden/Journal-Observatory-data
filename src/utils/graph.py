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
    return Graph(store=store, namespace_manager=nm, identifier=id)


def fuseki_graph(type="read", endpoint="https://localhost:3030/job", id=None, clear=False, nm=None):
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
            query_endpoint=f"{endpoint}/query"
        )
        graph = ConjunctiveGraph(store=db, identifier=id)
    if clear:
        if graph.__len__():
            print(f"cleared graph {graph.identifier} with {graph.__len__()} records")
            graph.update(f"clear graph <{graph.identifier}>")
    graph.namespace_manager = nm
    return graph
