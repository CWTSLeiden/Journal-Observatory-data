from utils.namespace import PADNamespaceManager
from utils.print import print_verbose
import requests
import json


def graphdb_add_namespaces(query_endpoint):
    if "/repositories/" in query_endpoint:
        print_verbose("Add namespaces to GraphDB")
        for prefix, uri in dict(PADNamespaceManager().namespaces()).items():
            if prefix not in ("this", "sub"):
                url = f"{query_endpoint}/namespaces/{prefix}"
                requests.put(url, data=uri)
        return True
    print_verbose("Endpoint is not a GraphDB instance, no namespaces added.")
    return False


def graphdb_setup_repository(graphdb_host : str, config_file : str, repo_id : str):
    rest = f"{graphdb_host}/rest/repositories"
    repositories = requests.get(rest)
    repo_exists = False
    for repository in json.loads(repositories.text):
        if repository.get("id") == repo_id:
            repo_exists = True
    if repo_exists:
        print_verbose(f"Repository already exists at {graphdb_host}/repositories/{repo_id}")
        return False
    print_verbose(f"Setup repository in GraphDB using {config_file}")
    req = requests.post(rest, files={"config": open(config_file, "rb")})
    if req.text == '':
        print_verbose(f"Repository created at {graphdb_host}/repositories/{repo_id}")
        return True
    else:
        print_verbose(f"Repository not created\n\n[{req.text}]")
        return False
