if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from tqdm import tqdm
from store.convert_doaj import convert_doaj
from store.convert_issnl import convert_issnl
from store.convert_openalex import convert_openalex
from store.convert_publisher_peer_review import convert_publisher_peer_review
from store.convert_sherpa_romeo import convert_sherpa_romeo
from store.convert_wikidata import convert_wikidata
from rdflib import Dataset
from utils.print import print_verbose
from utils.graphdb import graphdb_setup
from utils import pad_config
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

    
def convert_all(db: Dataset, debug=False):
    processes = (
        convert_doaj,
        convert_openalex,
        convert_publisher_peer_review,
        convert_sherpa_romeo,
        convert_issnl,
        convert_wikidata,
    )
    run(processes, db, debug)


if __name__ == "__main__":
    debug = pad_config.getboolean("main", "debug", fallback=False)
    pad_db = graphdb_setup(pad_config, "pad")
    convert_all(pad_db, debug)
