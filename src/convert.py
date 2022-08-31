import re
from namespace import JobNamespace
from store import json_to_graph
from utils.utils import file_to_json
from utils.graph import init_graph

def read_query_file(file):
    queries = []
    with open(file, "r") as query_file:
        querylines = query_file.read().split("\n")
    querylines = [ q for q in querylines if not re.search("^ *(#.*)?$", q) ]
    n = -1
    for line in querylines:
        if re.search("^construct ", line) or n < 0:
            n += 1; queries.append("")
        queries[n] += " " + line
    return queries
        

def graph_to_jobmap(graph, queries):
    jobnamespace = JobNamespace(uuid=True)
    jobmap_graph = init_graph(nm=jobnamespace)
    graph.namespace_manager = jobnamespace
    # graph.bind("this", jobnamespace.THIS, override=True)
    # graph.bind("sub", jobnamespace.SUB, override=True)

    for query in queries:
        jobmap_graph += graph.query(query)

    return jobmap_graph


def json_to_jobmap(journal_json, context, queries):
    graph = json_to_graph(journal_json, context)
    return graph_to_jobmap(graph, queries)


def json_file_to_jobmap(file, context_file, queries_file):
    journal_json = file_to_json(file)
    context = file_to_json(context_file)
    queries = read_query_file(queries_file)
    return json_to_jobmap(journal_json, context, queries)
        
