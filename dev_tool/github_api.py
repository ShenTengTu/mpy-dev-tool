import requests
import base64
from os import linesep
from collections import namedtuple
from . import realpath_join, path_exists, HERE, PYPROJECT_TOML
from .toml_op import read_toml, write_toml

_api_root = "https://api.github.com"

Gist = namedtuple("Gist", "gist_id sha")
Repo_Contents = namedtuple("Repo_Contents", "owner repo path")

git_source_choices = ["gists", "repo_contents"]


def single_gist(gist_id, sha=None):
    endpoint = "/".join((_api_root, "gists"))
    args = (endpoint, gist_id, sha) if type(sha) is str else (endpoint, gist_id)
    return "/".join(args)


def repo_get(owner, repo):
    args = (_api_root, "repos", owner, repo)
    return "/".join(args)


def repo_contents(owner, repo, path):
    args = (_api_root, "repos", owner, repo, "contents", path)
    return "/".join(args)


def api_response(url, params=None, **kwargs):
    resp = requests.get(url, params, **kwargs)
    resp_json = resp.json()
    if not resp.ok:
        raise requests.exceptions.RequestException(resp_json["message"])
    return resp_json


def git_revisions(resp_json: dict):
    return [h.get("version", None) for h in resp_json.get("history", [])]


def git_files(resp_json: dict):
    return resp_json.get("files", {})


def repo_contents_type(resp_json):
    """
    Types: dir, file, symlink, submodule
    """
    if type(resp_json) is list:
        return "dir"
    if type(resp_json) is dict:
        return resp_json.get("type", "unkown")
    return "unkown"


def make_script_from_base64(local_path, base64_content):
    with open(local_path, "w", newline=linesep) as f:
        content = base64.b64decode(base64_content).decode()
        f.write(content)


def _update_from_gist(meta, ref=None):
    file_path = realpath_join(HERE, meta["file"], normcase=False)
    file_exists = path_exists(file_path)
    args = Gist(meta["gist_id"], ref)
    if file_exists:
        args = Gist(args.gist_id, None)
    url = single_gist(*args)
    resp_json = api_response(url, headers={"Accept": "application/vnd.github.v3.base64"})
    r_files = git_files(resp_json)
    r_f = r_files.get(meta["file"], None)
    revisions = git_revisions(resp_json)

    if r_f is None:
        print("Not found %s in the gist" % meta["file"])
        return

    def _internal_handle():
        print("download %s" % r_f["raw_url"])
        make_script_from_base64(file_path, r_f["content"])
        # update meta reference
        meta["sha"] = revisions[0] if args.sha is None else args.sha

    if not file_exists:
        _internal_handle()
        return True
    else:
        if meta["sha"] != revisions[0]:
            _internal_handle()
        return True


def _update_from_repo_contents(meta, ref=None):
    file_path = realpath_join(HERE, meta["file"], normcase=False)
    file_exists = path_exists(file_path)
    args = Repo_Contents(*[meta.get(k, None) for k in Repo_Contents._fields])
    url = repo_contents(*args)
    params_ = {} if ref is None else {"ref": ref}
    resp_json = api_response(url, params=params_)
    rct = repo_contents_type(resp_json)

    def _internal_handle():
        print("download %s" % resp_json["download_url"])
        make_script_from_base64(file_path, resp_json["content"])
        if ref is None:
            repo_info = api_response(repo_get(args.owner, args.repo))
            meta["ref"] = repo_info["default_branch"]
        else:
            meta["ref"] = ref
        meta["sha"] = resp_json["sha"]  # update meta reference

    if not file_exists:
        if rct == "file":
            _internal_handle()
            return True
        else:
            return False
    else:
        if rct == "file":
            if meta["sha"] != resp_json["sha"]:
                _internal_handle()
                return True
        else:
            return False


def update_from_github(namespace, meta):
    """
    Try to download script file from github.
    Return True if update successful, or False if faild.
    """
    if namespace.source == git_source_choices[0]:
        return _update_from_gist(meta, namespace.ref)
    elif namespace.source == git_source_choices[1]:
        return _update_from_repo_contents(meta, namespace.ref)
    else:
        return

def update_script_from_github(namespace):
    d = read_toml(PYPROJECT_TOML)
    meta = None
    index = -1
    meta_list = d["dev_tool"]["script_src"][namespace.source]
    for meta_ in meta_list:
        index += 1
        if meta_.get("file", "") == namespace.file:
            meta = meta_
            break
    if meta is None:
        print("%s is not in pyproject.toml" % namespace.file)
        return

    success = update_from_github(namespace, meta)  # update meta reference if success
    if not success:
        return

    write_toml(PYPROJECT_TOML, d)
