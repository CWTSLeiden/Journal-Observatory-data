import requests
import json
import tarfile as tar
from os import path, makedirs, walk
from configparser import ConfigParser
from datetime import date

# Parse config file
# The config file should have 2 sections
# [import]
# url={url of the journal bulk file}
# dir={base directory for bulk import}
#     (A new subdirectory will be created in which the data will be deposited)
# compress={create an archive of the bulk data if true}

config = ConfigParser()
config.read("doaj_bulk.conf")

bulk_import_url = config.get("import", "url", fallback="https://doaj.org/public-data-dump/journal")
bulk_import_directory = config.get("import", "dir", fallback="~/")
bulk_import_compress = config.getboolean("import", "compress", fallback=False)
verbose = config.getboolean("import", "verbose", fallback=False)

datestamp = date.today().strftime("%Y%m%d")
import_dir = f"{bulk_import_directory}/{datestamp}_doaj"
data_archive = f"{import_dir}.tgz"
data_dir = f"{import_dir}/data"
extract_dir = f"{import_dir}/extract"


def dump_file(file_path, content):
    """
    Write results to file, creating a unique name if the path already exists.
    """
    file_name, extension = path.splitext(file_path)
    counter = 0
    while path.exists(file_path):
        counter += 1
        file_path = f"{file_name}_{counter}{extension}"
    with open(file_path, "w") as f:
        json.dump(content, f)


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


def doaj_download_bulk_file():
    """
    Download the Doaj bulk journal file and extract it.
    """
    tar_file = f"{import_dir}/doaj_journal_data.tar.gz"
    with requests.get(bulk_import_url, stream=True) as r:
        r.raise_for_status()
        with open(tar_file, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    if path.exists(tar_file):
        makedirs(extract_dir, exist_ok=True)
        with tar.open(tar_file) as t:
            t.extractall(extract_dir)


def doaj_parse_bulk_files():
    """
    Split the bulk journal file into individual records.
    """
    for root, _, files in walk(extract_dir):
        for file in files:
            _, extension = path.splitext(file)
            if extension == ".json":
                with open(path.join(root, file), "r") as f:
                    for record in json.load(f):
                        doaj_write_record_to_file(record)


def doaj_write_record_to_file(record):
    """
    Write the results of a query to a file with the preferred issn as file name.
    """
    id, _ = doaj_get_issns(record.get("bibjson"))
    dump_file(f"{data_dir}/{id}.json", record)
        

def compress_data_files(data_path, archive):
    with tar.open(archive, "w:gz") as t:
        for root, _, files in walk(data_path):
            for file in files:
                t.add(path.join(root, file))
            

if __name__ == "__main__":
    if path.exists(import_dir):
        print(f"Import directory {import_dir} exists")
        input("Press [Enter] to continue anyway.")
    makedirs(import_dir, exist_ok=True)
    makedirs(data_dir, exist_ok=True)
    doaj_download_bulk_file()
    doaj_parse_bulk_files()
    if bulk_import_compress:
        compress_data_files(data_dir, data_archive)
