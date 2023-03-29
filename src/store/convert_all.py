if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from store.convert_doaj import convert_doaj
from store.convert_issnl import convert_issnl
from store.convert_openalex import convert_openalex
from store.convert_publisher_peer_review import convert_publisher_peer_review
from store.convert_sherpa_romeo import convert_sherpa_romeo
from store.convert_wikidata import convert_wikidata
from rdflib import Dataset
from utils.graphdb import graphdb_setup
from utils import pad_config


def convert_all(db: Dataset, debug=False):
    convert_doaj(db, debug)
    convert_openalex(db, debug)
    convert_publisher_peer_review(db, debug)
    convert_sherpa_romeo(db, debug)
    convert_wikidata(db, debug)
    # convert_issnl(db, debug)


if __name__ == "__main__":
    debug = pad_config.getboolean("main", "debug", fallback=False)
    pad_db = graphdb_setup(pad_config, "test", recreate=True)
    convert_all(pad_db, debug)
