import requests
import json
import tarfile as tar
import os
from datetime import date
from bulk import dump_file, compress_data_files


def doaj_get_issns(doaj_bibjson):
    """
    Obtain the issn of a bibjson field of a DOAJ record.
    Returns a 'preferred' issn, which takes a single id with the preference:
        print_issn > electronic_issn > doaj_id
    and a dictionary of all issns
    """
    issns = {"id": [], "print": [], "electronic": []}
    issns["id"].append(doaj_bibjson.get("id"))
    issns["print"].append(doaj_bibjson.get("pissn"))
    issns["electronic"].append(doaj_bibjson.get("eissn"))
    issn = doaj_bibjson.get("pissn") or doaj_bibjson.get("eissn") or doaj_bibjson.get("id")
    return issn, issns


def doaj_download_bulk_file(url, destination):
    """
    Download the Doaj bulk journal file and extract it.
    """
    datestamp = date.today().strftime("%Y%m%d")
    tar_file = os.path.join(destination, f"doaj_journal_data_{datestamp}.tar.gz")
    extract_dir = os.path.join(destination, "extract")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(tar_file, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    if os.path.exists(tar_file):
        os.makedirs(extract_dir, exist_ok=True)
        with tar.open(tar_file) as t:
            t.extractall(extract_dir)


def doaj_parse_bulk_files(destination):
    """
    Split the bulk journal file into individual records.
    """
    extract_dir = os.path.join(destination, "extract")
    data_dir = os.path.join(destination, "data")
    os.makedirs(data_dir, exist_ok=True)
    for root, _, files in os.walk(extract_dir):
        for file in files:
            _, extension = os.path.splitext(file)
            if extension == ".json":
                with open(os.path.join(root, file), "r") as f:
                    for record in json.load(f):
                        doaj_write_record_to_file(record, data_dir)


def doaj_write_record_to_file(record, destination):
    """
    Write the results of a query to a file with the preferred issn as file name.
    """
    id, _ = doaj_get_issns(record.get("bibjson"))
    dump_file(os.path.join(destination, f"{id}.json"), record)
        

if __name__ == "__main__":
    from utils import job_config as config

    bulk_url = config.get("doaj", "bulk_url", fallback="https://doaj.org/public-data-dump/journal")
    bulk_dir = config.get("doaj", "bulk_path", fallback="~/")
    bulk_import_compress = config.getboolean("doaj", "bulk_compress", fallback=False)

    if os.path.exists(bulk_dir):
        print(f"Import directory {bulk_dir} exists")
    os.makedirs(bulk_dir, exist_ok=True)
    doaj_download_bulk_file(bulk_url, bulk_dir)
    doaj_parse_bulk_files(bulk_dir)
    if bulk_import_compress:
        datestamp = date.today().strftime("%Y%m%d")
        data_archive = os.path.join(bulk_dir, f"doaj_{datestamp}.tgz")
        compress_data_files(bulk_dir, data_archive)
