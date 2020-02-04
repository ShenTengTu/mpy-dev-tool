import os
import requests

here = os.path.dirname(__file__)
contents_url = "https://api.github.com/repos/ShenTengTu/mpy-dev-tool/contents/"


def api_response(url, params=None, **kwargs):
    resp = requests.get(url, params, **kwargs)
    resp_json = resp.json()
    if not resp.ok:
        raise requests.exceptions.RequestException(resp_json["message"])
    return resp_json


def download_script(download_url, local_file_path):
    r = requests.get(download_url, allow_redirects=True)
    with open(local_file_path, 'w', newline=os.linesep) as f:
        content = r.content.decode(r.encoding)
        f.write(content)
    print("downloaded %s" % download_url)


path_list = [
    "dev_tool",
    "pyproject.toml"
]

for r_path in path_list:
    local_path = os.path.join(here, r_path)
    resp_json = api_response(contents_url + r_path, params={"ref": "master"})
    if type(resp_json) is list:
        if not os.path.isdir(local_path):
            os.makedirs(local_path)
        for info in resp_json:
            if info["type"] == "file":
                local_path = os.path.join(here, info["path"])
                download_script(info["download_url"], local_path)
    elif type(resp_json) is dict:
        download_script(resp_json["download_url"], local_path)
