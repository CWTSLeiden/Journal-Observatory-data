from tqdm import tqdm
from store import (
    convert_doaj,
    convert_issnl,
    convert_openalex,
    convert_publisher_peer_review,
    convert_sherpa_romeo,
    convert_wikidata,
)
from utils.print import print_verbose
from utils.store import clear_default_graph, sparql_store_config, add_ontology
from utils.graphdb import graphdb_add_namespaces, graphdb_setup_repository
from utils import pad_config as config
from threading import Thread


def run(processes, db, debug=False, multithread=True):
    if multithread:
        threads = [Thread(target=p, args=[db, debug]) for p in processes]
        for t in threads:
            t.start()
        for t in tqdm(threads):
            t.join()
    else:
        for process in processes:
            process(db, debug)
    print_verbose("Done")


if __name__ == "__main__":
    debug = config.getboolean("main", "debug", fallback=False)

    graphdb_host = config.get("store", "host", fallback="http://localhost:7200")
    graphdb_config = config.getpath(
        "store", "config", fallback="config/graphdb-pad-config.ttl"
    )
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
    processes = (
        convert_doaj,
        convert_openalex,
        convert_publisher_peer_review,
        convert_sherpa_romeo,
        convert_issnl,
        convert_wikidata,
    )
    run(processes, db, debug)
