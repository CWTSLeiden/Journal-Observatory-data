from utils import bnode_to_sparql, init_graph
from configparser import ConfigParser
from glob import glob
from utils import ROOT_DIR, init_graph, ext_to_format
from tqdm import tqdm as progress
from rdflib.plugins.stores import sparqlstore
from doaj_convert import convert
from issnl_store import ISSNL_Store
from utils import print_graph


config = ConfigParser()
config.read(f"{ROOT_DIR}/config/job.conf")
doaj_dir = config.get("doaj", "bulk_path")
issnl_db = config.get("issnl", "db_path")
convert_file = config.get("doaj", "convert_file")
db_type = config.get("job", "db_type")
db_path = config.get("job", "db_path")
context_file = config.get("doaj", "context_file", fallback="")
db_max = 10
 
issnl_store = ISSNL_Store(db=issnl_db)

job_graph = init_graph(db_type=db_type, db_path=db_path, id="job")

files = glob(f"{doaj_dir}/rdf/*.ttl")

# for f in progress(files[:db_max]):
#     doaj_graph = init_graph()
#     doaj_graph.parse(f)
#     job_graph += convert(doaj_graph, convert_file, issnl_store)
#     job_graph.commit()

# job_graph.close()

doaj_graph = None
doaj_graph = init_graph()
doaj_graph.parse(files[3])
assertion = convert(doaj_graph, convert_file, issnl_store)
print_graph(assertion.query("construct {?s job:hasISSNL ?o } where { ?s job:hasISSNL ?o }"))
