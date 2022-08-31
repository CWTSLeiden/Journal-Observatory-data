import os
from store import bulk_to_graph, bulk_to_rdf


if __name__ == "__main__":
    from configparser import ConfigParser
    from glob import glob
    from utils.utils import ROOT_DIR, ext_to_format
    from utils.graph import init_graph

    config = ConfigParser()
    config.read(f"{ROOT_DIR}/config/job.conf")

    bulk_dir = config.get("doaj", "bulk_path", fallback="~/")
    
    context_file = config.get("doaj", "context_file", fallback="context.json")
    db_type = config.get("doaj", "db_type")
    db_path = config.get("doaj", "db_path")

    db_max = config.getint("doaj", "db_max", fallback=None)

    graph = init_graph(db_type=db_type, id="doaj", db_path=db_path, clear=True)
    files = glob(f"{bulk_dir}/data/*.json")
    print(files[0])
    graph = bulk_to_rdf(files=files,
                        destination=db_path,
                        context_file=context_file,
                        graph=graph,
                        max=db_max,
                        ext=db_type)
