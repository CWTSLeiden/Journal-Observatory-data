import requests
import json
import tarfile as tar
from os import path, makedirs, walk
from threading import Thread
from configparser import ConfigParser
from datetime import date

# Parse config file
# The config file should have 2 sections
# [api]
# url={base url of the api}
# key={personal API key}
# [import]
# dir={base directory for bulk import}
#     (A new subdirectory will be created in which the data will be deposited)
# compress={create an archive of the bulk data if true}

config = ConfigParser()
config.read("sherpa_romeo.conf")

api_base = config.get("api", "url", fallback="https://v2.sherpa.ac.uk/cgi")
api_key = config.get("api", "key", fallback="")
bulk_import_directory = config.get("import", "dir", fallback="~/")
bulk_import_compress = config.getboolean("import", "compress", fallback=False)

datestamp = date.today().strftime("%Y%m%d")
import_dir = f"{bulk_import_directory}/{datestamp}_sherpa_romeo"
data_archive = f"{import_dir}.tgz"
data_dir = f"{import_dir}/data"
log_file = f"{import_dir}/bulk_import.log"


def write_log(url, limit, offset, code):
    """
    Write a line in the log_file in tsv format.
    """
    if not path.exists(log_file):
        with open(log_file, "a") as f:
            f.write(f"return_code\toffset\tlimit\turl\n")
    with open(log_file, "a") as f:
        f.write(f"{code}\t{offset}\t{limit}\t{url}\n")


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


def sherpa_romeo_api_issn(issn):
    """
    Query the Sherpa Romeo API for a single record by ISSN.
    """
    api_url = (
        f"{api_base}/retrieve_by_id"
        f"?api-key={api_key}"
        f"&item-type=publication"
        f"&format=Json"
        f"&identifier={issn}"
    )
    result = requests.get(api_url)
    if result.status_code == 200:
        return json.loads(result.content)


def sherpa_romeo_api_bulk(limit=100, offset=0):
    """
    Query the Sherpa Romeo API for a number of records.
    limit:  Number of records ber batch. Maximum is 100.
    offset: Query starting at record number {offset}
    """
    limit = min(limit, 100)
    api_url = (
        f"{api_base}/retrieve"
        f"?api-key={api_key}"
        f"&item-type=publication"
        f"&format=Json"
        f"&limit={limit}"
        f"&offset={offset}"
    )
    result = requests.get(api_url)
    if result.status_code == 200:
        return api_url, result.status_code, json.loads(result.content)
    return api_url, result.status_code, None


def sherpa_romeo_import_bulk_file_thread(limit, offset, offset_multiplier, max=-1):
    """
    Create a loop to obtain multiple batches of records from the Sherpa Romeo API
    limit:  Number of records ber batch. Maximum is 100.
    offset: Query starting at record number {offset}
    offset_multiplier: Skip this number of records, multiplied by limit of records
                       Every batch.
    max:    Maximum number of records to query in total. Rounds to a multiple of limit.
    """
    records = [True]
    while records and (max < 0 or max > offset):
        print(f"get   items {offset} - {offset + limit}")
        url, code, content = sherpa_romeo_api_bulk(limit, offset)
        records = content.get("items")
        write_log(url, limit, offset, code)
        if code == 200 and records:
            print(f"write items {offset} - {offset + limit}")
            sherpa_romeo_write_records_to_file(records)
        if code != 200 and not records:
            print(f"Return code error")
            records = [True]
        offset = offset + (limit * offset_multiplier)
    print(f"Finished")


def sherpa_romeo_import_bulk_file(limit=100, offset=0, max=-1, thread_count=1):
    """
    Create {thread_count} threads to query the Sherpa Romeo API simultaneously.
    limit:  Number of records ber batch. Maximum is 100.
    offset: Query starting at record number {offset}
    max:    Maximum number of records to query in total. Rounds to a multiple of limit.
    thread_count: number of simultaneous queries to perform.
    """
    threads = []
    for i in range(thread_count):
        max_thread = max / thread_count
        threads.append(Thread(target=sherpa_romeo_import_bulk_file_thread,
                              args=(limit, offset, thread_count, max_thread),
                              name=f"thread_{i}"))
        offset = offset + limit
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def sherpa_romeo_get_issns(sherpa_romeo_issns):
    """
    Obtain the issn of a issns field of a Sherpa Romeo record.
    Returns a 'preferred' issn, which takes a single issn with the preference:
        print > electronic > none > legacy
    and a dictionary of all issns
    """
    def first(l):
        return l[0] if l else None
    issns = {"print": [], "electronic": [], "legacy": [], "none": []}
    for issn in sherpa_romeo_issns:
        if issn.get("type") in ("print", "electronic", "legacy"):
            issns[issn.get("type")].append(issn.get("issn"))
        else:
            issns["none"].append(issn.get("issn"))
    issn = (
        first(issns["print"]) or
        first(issns["electronic"]) or
        first(issns["none"]) or
        first(issns["legacy"])
    )
    return issn, issns


def compress_data_files(data_path, archive):
    with tar.open(archive, "w:gz") as t:
        for root, _, files in walk(data_path):
            for file in files:
                t.add(path.join(root, file))


def sherpa_romeo_write_records_to_file(records):
    """
    Write the results of a query to a file with the preferred issn as file name.
    """
    for record in records:
        issn, _ = sherpa_romeo_get_issns(record.get("issns"))
        dump_file(f"{data_dir}/{issn}.json", record)
            

if __name__ == "__main__":
    if not api_key:
        print(f"No API key set.")
        input("Press [Enter] to continue anyway.")
    if path.exists(import_dir):
        print(f"Import directory {import_dir} exists")
        input("Press [Enter] to continue anyway.")
    makedirs(import_dir, exist_ok=True)
    makedirs(data_dir, exist_ok=True)
    sherpa_romeo_import_bulk_file(limit=100, offset=0, max=-1, thread_count=10)
    if bulk_import_compress:
        compress_data_files(data_dir, data_archive)
