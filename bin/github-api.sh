#!/bin/sh
github_api_root="https://api.github.com"
github_header="Accept: application/vnd.github.v3+json"
record_path="$PWD/github-api.sh.json"

# response_handle_pyc <api> <python_script>
response_handle_pyc(){
    echo "$(curl -s -H "$github_header" "$1"  | python -c "import sys, json; RESP=json.load(sys.stdin);$2")"
}
 
# update_record_file_pyc <python_script>
update_record_file_pyc(){
    # init if not exist
     [ ! -f "$record_path" ] && echo "{\"repo_contents\": {},\"gists\":{}}" > $record_path
    # update
     python -c "import json; RECORD=json.load(open('$record_path', 'r')); $1; json.dump(RECORD, open('$record_path', 'w'), indent=4)"
}

#  _download_from_gist <api> <file_url> <revision> <local_path>
_download_from_gist(){
    echo "Download $2...\n[revision : $3]" && curl -# "$2" -o "$PWD/$4"
    update_record_file_pyc "d=RECORD['gists'];d.setdefault('$1', {});d['$1'].setdefault('files', {});d['$1']['files']['$4']='$2';d['$1']['revision']='$3'"
}

#  download_from_gist <gist_id> <file> <local_path>
download_from_gist(){
    local api="$github_api_root/gists/$1"
    local args="$(response_handle_pyc "$api" "file=RESP['files']['$2'];revision=[h['version'] for h in RESP['history']][0];print('$api', file['raw_url'], revision,'$3')")"
    _download_from_gist $args
}

# _download_repo_contents <api> <download_url> <sha> <local_path>
_download_repo_contents(){
    echo "Download $2...\n[sha : $3]" && curl -# "$2" -o "$PWD/$4"
    update_record_file_pyc "d=RECORD['repo_contents'];d.setdefault('$1', {});d['$1']['$4']='$2';d['$1']['sha']='$3'"
}

# download_repo_contents <owner> <repo> <remote_path> <local_path>
download_repo_contents(){
    local api="$github_api_root/repos/$1/$2/contents/$3"
    local args="$(response_handle_pyc "$api" "print('$api', RESP['download_url'], RESP['sha'], '$4')")"
    _download_repo_contents $args
}

  case $1 in
	download_repo_contents)
		download_repo_contents $2 $3 $4 $5
        break
		;;
    download_from_gist)
        download_from_gist $2 $3 $4
        break
        ;;
	*)
		echo ""
        break
		;;
  esac
