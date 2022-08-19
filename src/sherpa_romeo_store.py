import os
from rdflib import Namespace
from namespace import JobNamespace, ROMEO
from store import bulk_to_graph
from utils import ext_to_format

ROMEO_PUBLISHER = Namespace(f"{ROMEO}publisher/")
ROMEO_POLICY = Namespace(f"{ROMEO}publisher_policy/")
ROMEO_PUBLICATION = Namespace(f"{ROMEO}publication/")

class SherpaRomeoNamespace(JobNamespace):
    def __init__(self, uuid=False):
        super().__init__(uuid)

        self.bind("romeo-publisher", ROMEO_PUBLISHER)
        self.bind("romeo-policy", ROMEO_POLICY)
        self.bind("romeo-publication", ROMEO_PUBLICATION)


if __name__ == "__main__":
    from configparser import ConfigParser
    from glob import glob
    from utils import ROOT_DIR, init_graph

    config = ConfigParser()
    config.read(f"{ROOT_DIR}/config/job.conf")

    bulk_dir = config.get("sherpa_romeo", "bulk_path", fallback="~/")
    
    context_file = config.get("sherpa_romeo", "context_file", fallback="context.json")
    db_type = config.get("sherpa_romeo", "db_type")
    db_path = config.get("sherpa_romeo", "db_path")
    os.makedirs(db_path, exist_ok=True)

    db_max = int(config.get("sherpa_romeo", "db_max"))

    graph = init_graph(db_type=db_type,
                       id="sherpa_romeo",
                       db_path=db_path,
                       clear=True,
                       nm=SherpaRomeoNamespace())
    
    files = glob(f"{bulk_dir}/data/*.json")
    graph = bulk_to_graph(files=files,
                          context_file=context_file,
                          graph=graph,
                          max=db_max)
    if db_type in ["ttl", "jsonld"]:
        graph.serialize(os.path.join(db_path, f"sherpa_romeo.{db_type}"),
                        format=ext_to_format(db_type))
    graph.close()
