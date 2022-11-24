from store.convert import dataset_convert
from store.convert_issnl import dataset_convert_issnl
from utils.store import clear_default_graph, sparql_store


if __name__ == "__main__":
    graph = sparql_store(update=True)
    clear_default_graph(graph, confirm=True)
    dataset_convert("doaj")
    dataset_convert("openalex")
    dataset_convert("publisher_peer_review")
    dataset_convert("sherpa_romeo")
    dataset_convert_issnl()
