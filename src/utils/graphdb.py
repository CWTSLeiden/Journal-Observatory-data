from utils.namespace import PADNamespaceManager
from utils.print import print_verbose
import requests
import json


def graphdb_init(host, auth={}):
    if not requests.get(f"{host}/rest/security").json():
        print_verbose("Enable security policy")
        headers = {"Content-type": "application/json"}
        headers = graphdb_authorize(host, auth, headers)
        requests.patch(f"{host}/rest/security/users/admin", json=auth)
        requests.post(f"{host}/rest/security", data="true", headers=headers)
    else:
        print_verbose("Security policy already enabled")


def graphdb_set_free_access(host, repo_id, auth={}):
    headers = {"Content-type": "application/json"}
    headers = graphdb_authorize(host, auth, headers)
    r = requests.get(f"{host}/rest/security/free-access", headers=headers)
    data = r.json()
    data["enabled"] = True
    if not data.get("authorities"):
        data["authorities"] = []
    if f"READ_REPO_{repo_id}" not in data.get("authorities"):
        print_verbose(f"Set public read access for repo: {repo_id}")
        data["authorities"].append(f"READ_REPO_{repo_id}")
    requests.post(f"{host}/rest/security/free-access", json=data, headers=headers)


def graphdb_add_namespaces(host, repo_id, auth={}):
    headers = graphdb_authorize(host, auth)
    print_verbose("Add namespaces to GraphDB")
    for prefix, uri in dict(PADNamespaceManager().namespaces()).items():
        if prefix not in ("this", "sub"):
            url = f"{host}/repositories/{repo_id}/namespaces/{prefix}"
            requests.put(url, data=uri, headers=headers)
    return True


def graphdb_setup_repository(host: str, repo_id: str, config_file: str, auth={}):
    graphdb_init(host, auth)
    headers = graphdb_authorize(host, auth)
    rest = f"{host}/rest/repositories"
    repositories = requests.get(rest, headers=headers)
    for repository in json.loads(repositories.text):
        if repository.get("id") == repo_id:
            print_verbose(f"Repository already exists at {host}/repositories/{repo_id}")
            return False
    print_verbose(f"Setup repository in GraphDB using {config_file}")
    req = requests.post(
        rest, files={"config": open(config_file, "rb")}, headers=headers
    )
    if req.text == "":
        graphdb_set_free_access(host, repo_id, auth)
        print_verbose(f"Repository created at {host}/repositories/{repo_id}")
        return True
    else:
        print_verbose(f"Repository not created\n\n[{req.text}]")
        return False


def graphdb_authorize(host: str, auth: dict, headers={}):
    res = requests.post(f"{host}/rest/login", json=auth)
    auth_headers = {"authorization": res.headers.get("authorization", "")}
    headers.update(auth_headers)
    return headers
