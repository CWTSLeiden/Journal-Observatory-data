from store import convert_doaj , convert_issnl , convert_openalex , convert_publisher_peer_review , convert_sherpa_romeo, convert_wikidata
from utils.store import clear_default_graph, sparql_store_config, add_ontology
from utils.graphdb import graphdb_add_namespaces, graphdb_setup_repository
from utils import pad_config as config

if __name__ == "__main__":
    debug = config.getboolean("main", "debug", fallback=False)

    graphdb_host = config.get("store", "host", fallback="http://localhost:7200")
    graphdb_endpoint = config.get("store", "query", fallback=f"{graphdb_host}/repositories/pad")
    graphdb_config = config.getpath("store", "config", fallback="config/graphdb-pad-config.ttl")
    graphdb_username = config.get("store", "username", fallback="")
    graphdb_password = config.get("store", "password", fallback="")
    graphdb_auth = {}
    if graphdb_username and graphdb_password:
        graphdb_auth = {"username": graphdb_username, "password": graphdb_password}
    graphdb_setup_repository(graphdb_host, "pad", graphdb_config, auth=graphdb_auth)
    graphdb_add_namespaces(graphdb_host, "pad", auth=graphdb_auth)

    db = sparql_store_config(config, update=True)
    clear_default_graph(db, confirm=True)

    add_ontology(db)
    convert_functions = (
        convert_doaj,
        convert_openalex,
        convert_publisher_peer_review,
        convert_sherpa_romeo,
        convert_issnl,
        convert_wikidata
    )
    for convert_function in convert_functions:
        convert_function(db, debug=debug)
