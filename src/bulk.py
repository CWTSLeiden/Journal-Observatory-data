import tarfile as tar
import os
import json

def compress_data_files(data_path, archive):
    with tar.open(archive, "w:gz") as t:
        for root, _, files in os.walk(data_path):
            for file in files:
                t.add(os.path.join(root, file))


def dump_file(file_path, content, unique=True):
    """
    Write results to file, creating a unique name if the path already exists.
    """
    file_name, extension = os.path.splitext(file_path)
    if unique:
        counter = 0
        while os.path.exists(file_path):
            counter += 1
            file_path = f"{file_name}_{counter}{extension}"
    with open(file_path, "w") as f:
        json.dump(content, f)

