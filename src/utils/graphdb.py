from utils.namespace import PADNamespaceManager
from utils.print import print_verbose
import requests
import json


def graphdb_init(graphdb_host, auth={}):
    if not requests.get(f"{db}/rest/security").json():
        headers = {"Content-type": "application/json"}
        headers.update(graphdb_authorize(graphdb_host, auth))
        requests.patch(f"{graphdb_host}/rest/security/users/admin", json=auth)
        requests.post(f"{graphdb_host}/rest/security", data='true', headers=headers)


def graphdb_set_free_access(graphdb_host, repo_id, auth={}):
    headers = {"Content-type": "application/json"}
    headers.update(graphdb_authorize(graphdb_host, auth))
    r = requests.get(f"{graphdb_host}/rest/security/free-access", headers=headers)
    data = r.json()
    data["enabled"] = True
    if not data.get("authorities"): data["authorities"] = []
    if not f"READ_REPO_{repo_id}" in data.get("authorities"):
        data["authorities"].append(f"READ_REPO_{repo_id}")
    requests.post(f"{graphdb_host}/rest/security/free-access", json=data, headers=headers)


def graphdb_add_namespaces(graphdb_host, repo_id, auth={}):
    headers = {}
    if auth:
        headers.update(graphdb_authorize(graphdb_host, auth))
    print_verbose("Add namespaces to GraphDB")
    for prefix, uri in dict(PADNamespaceManager().namespaces()).items():
        if prefix not in ("this", "sub"):
            url = f"{graphdb_host}/repositories/{repo_id}/namespaces/{prefix}"
            requests.put(url, data=uri)
    return True


def graphdb_setup_repository(graphdb_host : str, repo_id : str, config_file : str, auth={}):
    graphdb_init(graphdb_host, auth)
    headers = {}
    if auth:
        headers.update(graphdb_authorize(graphdb_host, auth))
    rest = f"{graphdb_host}/rest/repositories"
    repositories = requests.get(rest, headers=headers)
    for repository in json.loads(repositories.text):
        if repository.get("id") == repo_id:
            print_verbose(f"Repository already exists at {graphdb_host}/repositories/{repo_id}")
            return False
    print_verbose(f"Setup repository in GraphDB using {config_file}")
    req = requests.post(rest, files={"config": open(config_file, "rb")}, headers=headers)
    if req.text == '':
        graphdb_set_free_access(graphdb_host, repo_id, auth)
        print_verbose(f"Repository created at {graphdb_host}/repositories/{repo_id}")
        return True
    else:
        print_verbose(f"Repository not created\n\n[{req.text}]")
        return False


def graphdb_authorize(graphdb_host : str, auth : dict):
    res = requests.post(f"{graphdb_host}/rest/login", json=auth)
    return {"authorization": res.headers.get("authorization")} 


db = "http://localhost:7200"
auth = {'username': 'admin', 'password': 'cwtsbramboomen'}
graphdb_init(db, auth)
