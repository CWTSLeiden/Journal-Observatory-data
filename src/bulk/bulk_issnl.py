import glob
import csv
import threading
from tqdm import tqdm as progress


def get_issnl_file(data_path):
    "Obtain the right file from the bulk import directory."
    file = glob.glob(f"{data_path}/*ISSN-to-ISSN-L.txt")
    try:
        return file[0]
    except IndexError:
        print("ISSN-to-ISSN-L.txt file not found. Please obtain it from https://issn.org")
        print(f"and store it in {data_path}/")
        return ""


def line_to_issnl(line, identicals=True):
    "Transform a line from the bulk file into a issn-l,issn tuple."
    if line.get("ISSN") and line.get("ISSN-L"):
        if not identicals and (line.get("ISSN") == line.get("ISSN-L")):
            return None
        return (line.get("ISSN-L"), line.get("ISSN"))
    return None


def issnl_parse_bulk_file(file, identicals=True):
    """
    Convert the bulk file into a set
    parameters:
        identicals: include records in the list where issnl == issn
    """
    store = []
    noprogress = threading.current_thread() is not threading.main_thread()
    with open(file, "r") as f:
        for line in progress(csv.DictReader(f, delimiter='\t'), desc="Parse bulk file", disable=noprogress):
            t = line_to_issnl(line, identicals)
            if t:
                store.append(t)
    return store

