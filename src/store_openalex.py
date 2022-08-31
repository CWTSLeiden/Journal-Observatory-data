import os
from store import bulk_to_graph


if __name__ == "__main__":
    from configparser import ConfigParser
    from glob import glob
    from utils.utils import ROOT_DIR, ext_to_format
    from utils.graph import init_graph

    config = ConfigParser()
    config.read(f"{ROOT_DIR}/config/job.conf")

    bulk_dir = config.get("openalex", "bulk_path", fallback="~/")
    
    context_file = config.get("openalex", "context_file", fallback="context.json")
    db_type = config.get("openalex", "db_type")
    db_path = config.get("openalex", "db_path")

    db_max = config.getint("openalex", "db_max", fallback=1)

    graph = init_graph(db_type=db_type, id="openalex", db_path=db_path, clear=True)
    files = glob(f"{bulk_dir}/data/*.json")
    graph = bulk_to_graph(files=files,
                          context_file=context_file,
                          graph=graph,
                          max=db_max)
    if db_type in ["ttl", "jsonld"]:
        graph.serialize(os.path.join(db_path, f"openalex.{db_type}"),
                        format=ext_to_format(db_type))
    graph.close()
