import requests
import json
import os
from threading import Thread
from datetime import date
from bulk import compress_data_files, dump_file


def write_log(bulk_dir, url, limit, offset, code):
    """
    Write a line in the log_file in tsv format.
    """
    datestamp = date.today().strftime("%Y%m%d")
    log_file = f"sherpa_romeo_bulk_{datestamp}.tsv"
    log_dir = os.path.join(bulk_dir, "log")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_file)
    if not os.path.exists(log_path):
        with open(log_path, "a") as f:
            f.write(f"return_code\toffset\tlimit\turl\n")
    with open(log_path, "a") as f:
        f.write(f"{code}\t{offset}\t{limit}\t{url}\n")


def sherpa_romeo_write_records_to_file(destination, records):
    """
    Write the results of a query to a file with the preferred issn as file name.
    """
    for record in records:
        issn, _ = sherpa_romeo_get_issns(record.get("issns"))
        dump_file(f"{destination}/{issn}.json", record)
            

def sherpa_romeo_api_issn(api_conf, issn):
    """
    Query the Sherpa Romeo API for a single record by ISSN.
    """
    api_base = api_conf.get("url")
    api_key = api_conf.get("key")
    api_conf = (
        f"{api_base}/retrieve_by_id"
        f"?api-key={api_key}"
        f"&item-type=publication"
        f"&format=Json"
        f"&identifier={issn}"
    )
    result = requests.get(api_conf)
    if result.status_code == 200:
        return json.loads(result.content)


def sherpa_romeo_api_bulk(api_conf, limit=100, offset=0):
    """
    Query the Sherpa Romeo API for a number of records.
    limit:  Number of records ber batch. Maximum is 100.
    offset: Query starting at record number {offset}
    """
    api_base = api_conf.get("url")
    api_key = api_conf.get("key")
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
        return api_conf, result.status_code, json.loads(result.content)
    return api_conf, result.status_code, {}


def sherpa_romeo_import_bulk_file_thread(api_conf, destination, limit, offset, offset_multiplier, max=-1):
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
        url, code, content = sherpa_romeo_api_bulk(api_conf, limit, offset)
        records = content.get("items")
        write_log(bulk_dir, url, limit, offset, code)
        if code == 200 and records:
            print(f"write items {offset} - {offset + limit}")
            sherpa_romeo_write_records_to_file(destination, records)
        elif code != 200 and not records:
            print("Return code error")
            records = [True]
        offset = offset + (limit * offset_multiplier)
    print("Finished")


def sherpa_romeo_import_bulk_file(api_conf, destination, limit=100, offset=0, max=-1, thread_count=1):
    """
    Create {thread_count} threads to query the Sherpa Romeo API simultaneously.
    limit:  Number of records ber batch. Maximum is 100.
    offset: Query starting at record number {offset}
    max:    Maximum number of records to query in total. Rounds to a multiple of limit.
    thread_count: number of simultaneous queries to perform.
    """
    data_dir = os.path.join(destination, "data")
    os.makedirs(data_dir, exist_ok=True)
    threads = []
    for i in range(thread_count):
        max_thread = max / thread_count
        threads.append(Thread(target=sherpa_romeo_import_bulk_file_thread,
                              args=(api_conf, data_dir, limit, offset, thread_count, max_thread),
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


if __name__ == "__main__":
    from utils.utils import job_config as config

    api_base = config.get("sherpa_romeo", "bulk_url", fallback="https://v2.sherpa.ac.uk/cgi")
    api_key = config.get("sherpa_romeo", "bulk_key", fallback="")
    bulk_dir = config.get("sherpa_romeo", "bulk_path", fallback="~/")
    bulk_import_compress = config.getboolean("sherpa_romeo", "bulk_compress", fallback=False)
    verbose = config.getboolean("main", "verbose", fallback=False)

    if not api_key:
        print(f"No API key set.")
    if os.path.exists(bulk_dir):
        print(f"Import directory {bulk_dir} exists")
    os.makedirs(bulk_dir, exist_ok=True)
    api_conf = {"url": api_base, "key": api_key}
    sherpa_romeo_import_bulk_file(api_conf, bulk_dir, limit=100, offset=0, max=-1, thread_count=10)
    if bulk_import_compress:
        datestamp = date.today().strftime("%Y%m%d")
        data_archive = os.path.join(bulk_dir, f"sherpa_romeo_{datestamp}.tgz")
        compress_data_files(bulk_dir, data_archive)
