from rdflib import ConjunctiveGraph, Graph
from utils.namespace import JobNamespace
import re


def get_mapping(key, mapping={}, reverse=False):
    if reverse:
        rev_mapping = mapping
        mapping = {}
        for k, v in rev_mapping:
            if type(v) == str:
                mapping[v] = k
    if not reverse:
        key = re.sub("[-/ _]", "", key)
    return mapping.get(key)


def job_graph(id=None, nm=None, store="default"):
    graph = ConjunctiveGraph(store=store, identifier=id)
    graph.namespace_manager = nm or JobNamespace()
    return graph


def add_graph_context(graph : ConjunctiveGraph, context : Graph):
    for subj, pred, obj in context:
        graph.add((subj, pred, obj, context.identifier))
