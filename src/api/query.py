from rdflib.graph import ConjunctiveGraph
from utils.graph import job_graph, add_graph_context
from utils.namespace import JobNamespace, PAD
from utils.query import get_single_result


def pad_from_id(db, id, sub=None) -> ConjunctiveGraph:
    id = PAD[id]
    graph = job_graph(nm=JobNamespace(this=id))
    if sub:
        add_graph_context(graph, db.get_context(f"{id}/{sub}"))
    else:
        add_graph_context(graph, db.get_context(f"{id}/head"))
        add_graph_context(graph, db.get_context(f"{id}/provenance"))
        add_graph_context(graph, db.get_context(f"{id}/assertion"))
        add_graph_context(graph, db.get_context(f"{id}/docinfo"))
    return graph


def pad_count(db, query="{?pad a ppo:PAD}") -> int:
    query = f"select (count(*) as ?count) where {query}"
    total = get_single_result(db.query(query))
    return int(total or 0)
