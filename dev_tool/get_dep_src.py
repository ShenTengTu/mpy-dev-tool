# Execute this script to get scripts that dev tool needed.
from argparse import Namespace
from . import realpath_join, HERE
from .github_api import update_script_from_github

script_src_toml = realpath_join(HERE, "./script_src.toml")
update_script_from_github(
    Namespace(source='gists', file='cli.py', ref=None),
    config_toml=script_src_toml
    )
update_script_from_github(
    Namespace(source='repo_contents', file='pyboard.py', ref=None),
    config_toml=script_src_toml
    )