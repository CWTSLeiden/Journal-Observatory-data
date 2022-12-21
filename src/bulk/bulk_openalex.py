import requests
import json
import os
from datetime import date
from bulk import compress_data_files, dump_file


def write_log(bulk_dir, url, limit, cursor, code):
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
            f.write(f"return_code\tcursor\tlimit\turl\n")
    with open(log_path, "a") as f:
        f.write(f"{code}\t{cursor}\t{limit}\t{url}\n")


def openalex_api_cursor(api_base, cursor="*", email=None):
    api_url = (
        f"{api_base}"
        f"?cursor={cursor}"
        f"&per_page=200"
    )
    if email: api_url += f"&mailto={email}"
    result = requests.get(api_url)
    if result.status_code == 200:
        content = json.loads(result.content)
        next_cursor = content.get("meta").get("next_cursor")
        return next_cursor, result.status_code, content
    return cursor, result.status_code, {}


def openalex_write_records_to_file(destination, records):
    """
    Write the results of a query to a file with the preferred issn as file name.
    """
    for record in records.get("results"):
        id = record.get("id").replace("https://openalex.org/", "")
        dump_file(f"{destination}/{id}.json", record)


def openalex_api_bulk(api_conf, destination):
    data_dir = os.path.join(destination, "data")
    os.makedirs(data_dir, exist_ok=True)

    cursor = "*"
    api_url = api_conf.get("url")
    api_email = api_conf.get("email")
    while cursor:
        next_cursor, code, results = openalex_api_cursor(api_base=api_url,
                                                         cursor=cursor,
                                                         email=api_email)
        write_log(bulk_dir, api_url, "200", cursor, code)
        if code == 200 and results:
            print(f"OK: {api_url}?{cursor}")
            openalex_write_records_to_file(data_dir, results)
        elif code != 200:
            print(f"Return code error: {code}")
            break
        cursor = next_cursor
    print("Finished")


if __name__ == "__main__":
    from utils import job_config as config

    email = config.get("main", "email")
    bulk_url = config.get("openalex", "bulk_url", fallback="https://api.openalex.org/venues")
    bulk_dir = config.getpath("openalex", "bulk_path", fallback="~/")
    bulk_import_compress = config.getboolean("openalex", "bulk_compress", fallback=False)
    verbose = config.getboolean("main", "verbose", fallback=False)

    if os.path.exists(bulk_dir):
        print(f"Import directory {bulk_dir} exists")
    os.makedirs(bulk_dir, exist_ok=True)
    api_conf = {"url": bulk_url, "email": email }
    openalex_api_bulk(api_conf, bulk_dir)
    if bulk_import_compress:
        datestamp = date.today().strftime("%Y%m%d")
        data_archive = os.path.join(bulk_dir, f"openalex_{datestamp}.tgz")
        compress_data_files(bulk_dir, data_archive)
