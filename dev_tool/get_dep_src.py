# Execute this script to get scripts that dev tool needed.
from argparse import Namespace
from .github_api import update_script_from_github

update_script_from_github(Namespace(source='gists', file='cli.py', ref=None))
update_script_from_github(Namespace(source='repo_contents', file='pyboard.py', ref=None))