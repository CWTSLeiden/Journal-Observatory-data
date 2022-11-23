from rdflib import ConjunctiveGraph
from namespace import JobNamespace


def job_graph(id=None, nm=None, store="default"):
    graph = ConjunctiveGraph(store=store, identifier=id)
    graph.namespace_manager = nm or JobNamespace()
    return graph
