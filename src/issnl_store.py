import glob
import csv
import os
from configparser import ConfigParser
from rdflib import Graph
from utils import ROOT_DIR
from namespace import ISSN
from tqdm import tqdm as progress


def load_issnl_file(bulk_dir):
    "Obtain the right file from the bulk import directory."
    file = glob.glob(f"{bulk_dir}/*ISSN-to-ISSN-L.txt")
    try:
        return file[0]
    except IndexError:
        print("ISSN-to-ISSN-L.txt file not found. Please obtain it from https://issn.org")
        print(f"and store it in {bulk_dir}/")
        return None


def line_to_issnl(line, filter=None):
    "Transform a line from the bulk file into a issn-l,issn tuple."
    if line.get("ISSN") and line.get("ISSN-L"):
        if not filter or line.get("ISSN") in filter:
            return (line.get("ISSN-L"), line.get("ISSN"))
    return None


def issnl_parse_bulk_file(bulk_dir, filter=None):
    """
    Convert the bulk file into a set
    parameters:
        filter: A list of issns to be included in the store
        location: An alternative location for the resulting csv-file
            (default: [import].[db] from config)
    """
    store = set()
    file = load_issnl_file(bulk_dir)
    if file and progress:
        with open(file, "r") as f:
            for line in progress(csv.DictReader(f, delimiter='\t'), desc="Parse bulk file"):
                t = line_to_issnl(line, filter)
                if t:
                    store.add(t)
    return store


class ISSNL_Store():
    def __init__(self, db="issnl.csv", store=set(), graph=Graph()):
        self.db = db
        self.store = store
        self.graph = graph
        self.graph.bind("issn", ISSN)

    def write(self, overwrite=False):
        if not os.path.exists(self.db) or overwrite:
            with open(self.db, "w") as f:
                for s in progress(self.store, desc=f"Write store to {self.db}"):
                    f.write(",".join(s) + "\n")
        else:
            print(f"{self.db} already exists, pass 'overwrite=True' to overwrite")

    def parse_bulk(self, bulk_dir):
        self.store = issnl_parse_bulk_file(bulk_dir)

    def open(self, filter=None):
        """
        Return the store as a set of tuples
        Create the store if it does not exist
        """
        if not self.store:
            try:
                with open(self.db, "r") as f:
                    file = csv.reader(f, delimiter=',')
                    self.store = set(progress(map(tuple, file), desc="Load ISSNL db"))
            except FileNotFoundError:
                print(f"Database file not found: {self.db}")
        if filter:
            filtered_store = set()
            for s in self.store:
                if s[1] in filter:
                    filtered_store.add(s)
            return filtered_store
        return self.store

    def open_graph(self, filter=None):
        """
        Return the store as a graph
        Create the store if it does not exist
        """
        store = self.open(filter=filter)
        for issnl, issn in store:
            self.graph.add((ISSN[issnl], ISSN["ISSNLof"], ISSN[issn]))
        return self.graph


if __name__ == "__main__":
    config = ConfigParser()
    config.read(f"{ROOT_DIR}/config/job.conf")

    bulk_dir = config.get("issnl", "bulk_path", fallback="~/issnl")
    issnl_db = config.get("issnl", "db_path", fallback="~/")

    issnl_store = ISSNL_Store(db=issnl_db)
    issnl_store.parse_bulk(bulk_dir)
    issnl_store.write(overwrite=True)
