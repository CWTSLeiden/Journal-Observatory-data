import requests
import json
import os
from datetime import date
from bulk import compress_data_files, dump_file


def write_log(data_path, url, limit, cursor, code):
    """
    Write a line in the log_file in tsv format.
    """
    datestamp = date.today().strftime("%Y%m%d")
    log_file = f"sherpa_romeo_bulk_{datestamp}.tsv"
    log_dir = os.path.join(data_path, "log")
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
        write_log(data_path, api_url, "200", cursor, code)
        if code == 200 and results:
            print(f"OK: {api_url}?{cursor}")
            openalex_write_records_to_file(data_dir, results)
        elif code != 200:
            print(f"Return code error: {code}")
            break
        cursor = next_cursor
    print("Finished")


if __name__ == "__main__":
    from utils import pad_config as config

    email = config.get("main", "email", fallback="")
    data_location = config.get("openalex", "data_location", fallback="https://api.openalex.org/venues")
    data_path = config.getpath("openalex", "data_path", fallback="data/openalex")
    bulk_import_compress = config.getboolean("openalex", "data_compress", fallback=False)
    verbose = config.getboolean("main", "verbose", fallback=False)

    if os.path.exists(data_path):
        print(f"Import directory {data_path} exists")
    os.makedirs(data_path, exist_ok=True)
    api_conf = {"url": data_location, "email": email }
    openalex_api_bulk(api_conf, data_path)
    if bulk_import_compress:
        datestamp = date.today().strftime("%Y%m%d")
        data_archive = os.path.join(data_path, f"openalex_{datestamp}.tgz")
        compress_data_files(data_path, data_archive)
