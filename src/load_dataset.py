from store import convert_doaj , convert_issnl , convert_openalex , convert_publisher_peer_review , convert_sherpa_romeo, convert_wikidata
from utils.store import clear_default_graph, sparql_store, add_ontology
from utils.graphdb import graphdb_add_namespaces, graphdb_setup_repository
from utils import job_config as config

if __name__ == "__main__":
    debug = config.getboolean("main", "debug", fallback=False)

    graphdb_host = config.get("store", "host", fallback="http://localhost:7200")
    graphdb_endpoint = config.get("store", "endpoint", fallback=f"{graphdb_host}/repositories/job")
    graphdb_config = config.getpath("store", "config", fallback="config/graphdb-job-config.ttl")
    graphdb_setup_repository(graphdb_host, graphdb_config, "job")
    graphdb_add_namespaces(graphdb_endpoint)

    graph = sparql_store(update=True)
    clear_default_graph(graph, confirm=True)

    add_ontology(graph)
    convert_doaj(debug=debug)
    convert_openalex(debug=debug)
    convert_publisher_peer_review(debug=debug)
    convert_sherpa_romeo(debug=debug)
    convert_issnl(debug=debug)
    convert_wikidata(debug=debug)
