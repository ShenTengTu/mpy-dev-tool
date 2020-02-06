import mpy_cross
from subprocess import PIPE
from . import realpath_join, mkdir, os_walk


def mpy_cross_process(*args):
    with mpy_cross.run(*args, stdout=PIPE) as proc:
        while True:
            line = proc.stdout.readline().decode("utf-8")
            if not line:
                break
            print(line.rstrip())


def mpy_cross_version():
    args = ("--version",)
    mpy_cross_process(*args)


def mk_mpy(src, dist):
    args = ("-o", dist, src)
    mpy_cross_process(*args)


def os_walk_mpy(src_dir, dist_dir=""):
    _args_list = []
    for dir_path, _, file_names in os_walk(src_dir):
        if dir_path.endswith("__pycache__"):
            continue

        dist_path = dir_path.replace(src_dir, dist_dir)
        mkdir(dist_path)

        for file_name in file_names:
            if not file_name.endswith(".py"):
                continue
            _args_list.append(
                (
                    realpath_join(dir_path, file_name),
                    realpath_join(dist_path, file_name.replace(".py", ".mpy")),
                )
            )
    return _args_list
