from store.convert_all import convert_all
from prototype.unify_pads import store_pads
from utils.graphdb import graphdb_setup
from utils import job_config, pad_config


if __name__ == "__main__":
    debug = job_config.getboolean("main", "debug", fallback=False)
    pad_db = graphdb_setup(pad_config, "pad", recreate=True)
    job_db = graphdb_setup(job_config, "job", recreate=True)
    convert_all(pad_db, debug=debug)
    store_pads(pad_db, job_db, debug=debug)
