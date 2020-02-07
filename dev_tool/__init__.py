import os
import shutil
import hashlib

__version__ = '0.1.0-beta'

# path util #
def os_cwd():
    return os.getcwd()

def replace_os_sep(path, new_sep="/"):
    return path.replace(os.sep, new_sep)


def dirname(path):
    return replace_os_sep(os.path.dirname(path))


def realpath(path, normcase=True):
    p = os.path.realpath(path)
    if normcase:
        return replace_os_sep(os.path.normcase(p))
    return replace_os_sep(p)


def realpath_join(root, *paths, normcase=True):
    return realpath(os.path.join(root, *paths), normcase)


def relpath(path, start=None):
    return replace_os_sep(os.path.relpath(path, start) if start else os.path.relpath(path))


def path_isdir(path):
    return os.path.isdir(path)


def lsdir(path):
    return os.listdir(path)


def mkdir(path):
    if not path_isdir(path):
        os.makedirs(path)


def os_walk(path):
    return os.walk(path)


def path_exists(path):
    return os.path.exists(path)


def path_basename(path):
    return os.path.basename(path)


def path_split(path):
    return os.path.split(path)


def os_strerror(code):
    return os.strerror(code)

def cp_file(src, dst):
    shutil.copyfile(src, dst)

def cp_dir(src, dst):
    try:
        shutil.copytree(src, dst)
    except FileExistsError:
        shutil.rmtree(dst)
        shutil.copytree(src, dst)

def os_walk_cp(src_dir, dest_dir, copy_fn=print):
    """
    `copy_fn(src, dest, isdir)`
    """
    dest_dir_ = dest_dir[:-1] if dest_dir.endswith("/") else dest_dir
    tree = os_walk(src_dir)
    for root, _, files in tree:
        root_ = replace_os_sep(root)
       
        # for dir
        rel_root = relpath(root_, start=src_dir)
        if rel_root != ".":
            if path_exists(root_):
                if callable(copy_fn):
                    copy_fn(root_, dest_dir_ + "/" + rel_root, True)  # src, dest, isdir
        
        # for file
        for f_nanme in files:
            src = realpath_join(root_, f_nanme)
            rel_src = relpath(src, start=src_dir)
            dest = dest_dir_ + "/" + rel_src
            if callable(copy_fn):
                if path_exists(src):
                    copy_fn(src, dest, False)  # src, dest, isdir


def fname_cp_dest(src, dest):
    # same function defined in `pyboard.py`
    src = src.rsplit("/", 1)[-1]
    if dest is None or dest == "":
        dest = src
    elif dest == ".":
        dest = "./" + src
    elif dest.endswith("/"):
        dest += src
    return dest


# file hash #


def file_hash(path):
    m = hashlib.md5()
    with open(path, "rb") as f:
        buf = f.read()
        m.update(buf)
    return m.hexdigest()


def os_walk_hash(dir_path):
    tree = os_walk(dir_path)
    d = {}
    for root, _, files in tree:
        for f_nanme in files:
            p = realpath_join(root, f_nanme)
            h = file_hash(p)
            d[relpath(p, start=dir_path)] = h
    return d


# config #
HERE = dirname(__file__)
DIST_DIR = realpath_join(HERE, "../dist")
SUBMODULES_DIR = realpath_join(HERE, "../submodules") # sub modules insides of main module
EXT_LIB_DIR = realpath_join(HERE, "../ext_lib") # for micropython-lib
LIB_DIR = realpath_join(HERE, "../lib") # for 3rd party Lib
ASSETS_DIR = realpath_join(HERE, "../assets")
PYPROJECT_TOML = realpath_join(HERE, "../pyproject.toml")