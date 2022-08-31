from os import path
import shutil
from rdflib import Graph
from namespace import JobNamespace
from rdflib.plugins.stores import sparqlstore
from rdflib import BNode


def bnode_to_sparql(node):
   if isinstance(node, BNode):
       return f"<bnode:b{node}>"
   return sparqlstore._node_to_sparql(node)


class ExtGraph(Graph):
    """
    Extension methods to the default RDFlib Graph
    """

    def clear(self):
        self.update(f"clear graph <{self.identifier}>")

    def create_graph(self):
        self.store.add_graph(self)

    def insert_graph(self, graph : Graph):
        "A more efficient alternative to Graph.__add__"
        self.update(f"INSERT DATA {{ {graph.serialize(format='nt')} }}")


def init_graph(db_type="", db_path=None, id=None, clear=True, nm=None):
    if not nm:
        nm = JobNamespace()
    if db_type in ["BerkeleyDB"] and db_path:
        db = path.join(db_path, f"{id}.berkeleydb")
        if clear and path.exists(db):
            shutil.rmtree(db)
        graph = ExtGraph(store=db_type, namespace_manager=nm, identifier=id)
        graph.open(db, create=clear)
        return graph
    elif db_type in ["fuseki"]:
        db = sparqlstore.SPARQLUpdateStore(
            query_endpoint=f"{db_path}/query",
            update_endpoint=f"{db_path}/update",
            node_to_sparql=bnode_to_sparql,
            auth=('admin','test')
        )
        graph = ExtGraph(store=db, namespace_manager=nm, identifier=id)
        return graph
    elif db_type in ["blazegraph"]:
        db = sparqlstore.SPARQLUpdateStore(
            query_endpoint=db_path,
            update_endpoint=db_path,
            node_to_sparql=bnode_to_sparql
        )
        graph = ExtGraph(store=db, namespace_manager=nm, identifier=id)
        return graph
    return ExtGraph(namespace_manager=nm, identifier=id)
