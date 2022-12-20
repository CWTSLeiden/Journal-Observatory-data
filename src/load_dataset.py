from store import convert_doaj , convert_issnl , convert_openalex , convert_publisher_peer_review , convert_sherpa_romeo, convert_wikidata
from utils.store import clear_default_graph, graphdb_add_namespaces, sparql_store, add_ontology
from utils.utils import job_config as config

if __name__ == "__main__":
    debug = config.getboolean("main", "debug", fallback=False)
    graph = sparql_store(update=True)
    clear_default_graph(graph, confirm=True)
    graphdb_add_namespaces(graph.store.query_endpoint)
    add_ontology(graph)
    convert_doaj(debug=debug)
    convert_openalex(debug=debug)
    convert_publisher_peer_review(debug=debug)
    convert_sherpa_romeo(debug=debug)
    convert_issnl(debug=debug)
    convert_wikidata(debug=debug)
