from rdflib import ConjunctiveGraph, Graph
from utils.namespace import PADNamespaceManager
import re


def pad_graph(id=None, nm=None, store="default"):
    graph = ConjunctiveGraph(store=store, identifier=id)
    graph.namespace_manager = nm or PADNamespaceManager()
    return graph


def add_graph_context(graph : ConjunctiveGraph, context : Graph):
    for subj, pred, obj in context:
        graph.add((subj, pred, obj, context.identifier))
