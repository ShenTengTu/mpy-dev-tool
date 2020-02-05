from argparse import _SubParsersAction, Namespace
import shutil
from os import linesep
from . import (
    realpath_join,
    os_walk_cp,
    os_walk_hash,
    path_exists,
    path_basename,
    HERE,
    DIST_DIR,
    SUBMODULES_DIR,
    EXT_LIB_DIR,
    LIB_DIR,
    PYPROJECT_TOML,
)
from .toml_op import write_toml, read_toml
from .mpy import mpy_cross_version, mk_mpy, os_walk_mpy
from .github_api import git_source_choices, update_from_github
from .pyb_util import PyboardContextbuilder
from .cli import CLI



def init_dev_tool_toml():
    d = read_toml(PYPROJECT_TOML)
    if "dev_tool" not in d:
        d.setdefault("dev_tool", {})

        d["dev_tool"].setdefault("module", {})
        d["dev_tool"]["module"].setdefault("name", "module_name")
        d["dev_tool"]["module"].setdefault("src_dir", ".")
        d["dev_tool"]["module"].setdefault("micropython-lib", [])

        d["dev_tool"].setdefault("submodule_dependencies", {})

        d["dev_tool"].setdefault("script_src", {})
        d["dev_tool"]["script_src"].setdefault(
            "gists", [{"file": "", "gist_id": "", "sha": ""}]
        )
        d["dev_tool"]["script_src"].setdefault(
            "repo_contents",
            [{"file": "", "owner": "", "repo": "", "path": "", "ref": "", "sha": ""}],
        )

        write_toml(PYPROJECT_TOML, d)

class PyBoardActioin(_SubParsersAction):
    """
    Create `PyboardContextbuilder` instance & add into the namespace.
    """

    # Must inherit "_SubParsersAction", because it is invoked in subparsers
    def __init__(self, option_strings, dest, **kwargs):
        # Fix TypeError: __init__() got multiple values for argument 'prog'
        kwargs.pop("prog", None)
        super().__init__(option_strings, dest, **kwargs)
        self.dest = dest  # Let the namespace contains the parser name

    def __call__(self, parser, namespace, values, option_string=None):
        super().__call__(parser, namespace, values, option_string)
        sub_parser_name = str(getattr(namespace, self.dest))
        if sub_parser_name.startswith(("pyboard_", "pyb_")):
            setattr(
                namespace,
                "_pyb_context_builder_",
                PyboardContextbuilder(
                    namespace.port,
                    namespace.baud,
                    namespace.user,
                    namespace.password,
                    namespace.wait,
                ),
            )

# #
MODULE_NAME = None
SRC_DIR = None

# CLI setting #
parser = CLI(
    main_params=dict(prog="dev_tool", description="Dev tool"),
    sub_params=dict(
        title="Task Commads",
        metavar="task_commad",
        description="All dev tasks as below.",
        dest="Task",
        required=True,
        action=PyBoardActioin,
    ),
)

# PyBoard arguments #
pyboard_args_g = parser.add_argument_group("PyBoard arguments")
pyboard_args_g.add_argument(
    "-p",
    "--port",
    default="/dev/ttyACM0",
    help="the serial device or the IP address of the pyboard",
)
pyboard_args_g.add_argument(
    "-b", "--baud", default=115200, help="the baud rate of the serial device"
)
pyboard_args_g.add_argument(
    "-u", "--user", default="micro", help="the telnet login username"
)
pyboard_args_g.add_argument(
    "-pw", "--password", default="python", help="the telnet login password"
)
pyboard_args_g.add_argument(
    "-w",
    "--wait",
    default=0,
    type=int,
    help="seconds to wait for USB connected board to become available",
)
pyboard_args_g.add_argument(
    "-dl", "--delay", default=3, type=int, help="seconds to wait before entering raw REPL"
)

# Task commands #
@parser.sub_command(
    aliases=["dl_ext"], help="download extra libraries to local from `micropython-lib`"
)
def download_ext_libs(args):

    def file_filter(file_info):
        file_name = str(file_info["name"])
        return (
            file_name.endswith(".py") 
            and not file_name.startswith(("test_", "example_"))
            and file_name not in ["setup.py"]
        )

    d = read_toml(PYPROJECT_TOML)
    if "micropython-lib" in  d["dev_tool"]["module"]:
        ext_lib_list = d["dev_tool"]["module"]["micropython-lib"]
        ns = Namespace(
            source='repo_contents',
            ref='master',
            parent_dir=EXT_LIB_DIR,
            file_filter=file_filter
            )
        meta = {
            'owner': 'micropython',
            'repo': 'micropython-lib',
            'file': None,
            'path': None,
            'sha': None
        }
    for lib_name in ext_lib_list:
        print(lib_name, ":")
        meta['file'] = lib_name
        meta['path'] = lib_name
        update_from_github(ns, meta)
        # create __init__.py
        init_py_path =  realpath_join(EXT_LIB_DIR, lib_name, "__init__.py", normcase=False)
        if not path_exists(init_py_path):
            with open(init_py_path, 'w', newline=linesep) as f:
                f.write("")

@parser.sub_command_arg(
    "submodule",
    help="relative path of the submodule src directory in `submodules` folder.",
    type=str,
)
@parser.sub_command(
    aliases=["a_sub"], help="add a submodule into main module ."
)
def add_submodule(args):
    submodule = args.submodule
    submodule_dir = realpath_join(SUBMODULES_DIR, submodule)
    if not path_exists(submodule_dir):
        print("The submodule is not exist : `%s`" % submodule_dir)
        return
    basename = path_basename(submodule_dir)
    dst_dir = realpath_join(SRC_DIR, basename)
    try:
        shutil.copytree(submodule_dir, dst_dir)
    except FileExistsError:
        print("`%s` has been exist." % basename)
        return
    # record sub module dependencies into `pyproject.toml`
    d = read_toml(PYPROJECT_TOML)
    d["dev_tool"]["submodule_dependencies"][basename] = submodule
    write_toml(PYPROJECT_TOML, d)
    print("add sub module : `%s`" % basename)


@parser.sub_command_arg(
    "submodule_name", help="submodule name in main module folder.", type=str
)
@parser.sub_command(
    aliases=["u_sub"], help="update a submodule in main module ."
)
def update_submodule(args):
    # read submodule_dependencies from PYPROJECT_TOML
    submodule_name = args.submodule_name
    d = read_toml(PYPROJECT_TOML)
    submodule = d["dev_tool"]["submodule_dependencies"].get(submodule_name, None)
    if submodule is None:
        print("Use `dev_tool add_submodule <submodule>` first.")
        return

    submodule_dir = realpath_join(SUBMODULES_DIR, submodule)
    if not path_exists(submodule_dir):
        print("The submodule is not exist : `%s`" % submodule_dir)
        return

    basename = path_basename(submodule_dir)
    dst_dir = realpath_join(SRC_DIR, basename)
    # get hash of each files by os_walk()
    d_src = os_walk_hash(submodule_dir)
    d_dst = os_walk_hash(dst_dir)
    # compare hash then update files
    for rel_path in d_src:
        if d_src[rel_path] == d_dst[rel_path]:
            continue
        src_f = realpath_join(submodule_dir, rel_path)
        dst_f = realpath_join(dst_dir, rel_path)
        shutil.copy2(src_f, dst_f)
        print("Upadate `%s`" % dst_f)


@parser.sub_command(
    aliases=["mk_mpy"], help="compile source `*.py` to `*.mpy` (save in `dist/mpy` folder)."
)
def make_mpy(args):
    args_list = os_walk_mpy(SRC_DIR, realpath_join(DIST_DIR, "mpy/" + MODULE_NAME))
    mpy_cross_version()
    while args_list:
        args = args_list.pop()
        mk_mpy(*args)
    print("finished.")


@parser.sub_command_arg("file", help="script file basename.", type=str)
@parser.sub_command_arg("source", help="the script source", choices=git_source_choices)
@parser.sub_command_arg("-r", "--ref", help="The name of the commit/branch/tag", type=str)
@parser.sub_command_arg("-d", "--dev", help="for dev_tool", action="store_true")
@parser.sub_command(
    aliases=["u_scpt"], help="update the script file by github API (see pyproject.toml)."
)
def update_script(args):
    if args.dev:
        d = read_toml(PYPROJECT_TOML)
        meta = None
        index = -1
        meta_list = d["dev_tool"]["script_src"][args.source]
        for meta_ in meta_list:
            index += 1
            if meta_.get("file", "") == args.file:
                meta = meta_
                break
        if meta is None:
            print("%s is not in pyproject.toml" % args.file)
            return

        success = update_from_github(args, meta)  # update meta reference if success
        if not success:
            return

        write_toml(PYPROJECT_TOML, d)

    else:
        print("only support `update_script --dev file`")


@parser.sub_command_arg("src", help="the dir path on the board", nargs="?", default="/")
@parser.sub_command(aliases=["pyb_ls"], help="pyboard: list the dir")
def pyboard_ls(args):
    with args._pyb_context_builder_(args.delay) as pyb_context:
        pyb_context.pyb.fs_ls(args.src)


@parser.sub_command(
    aliases=["pyb_i"], help="pyboard: install mpy distribution to the board"
)
def pyboard_install(args):
    with args._pyb_context_builder_(args.delay) as pyb_context:

        def copy_fn(src, dest, isdir):
            if isdir:
                pyb_context.mk_dir(dest, verbose=False)
            else:
                print("%s >> %s" % (src, dest))
                pyb_context.pyb.fs_put(src, dest)

        dest_dir = "lib/" + MODULE_NAME
        pyb_context.mk_dirs(dest_dir)
        src_dir = realpath_join(DIST_DIR, "mpy/" + MODULE_NAME)
        os_walk_cp(src_dir, dest_dir, copy_fn)


def main():
    parser.handle_args()


if __name__ == "__main__":
    init_dev_tool_toml()

    # get src dir path
    d = read_toml(PYPROJECT_TOML)
    MODULE_NAME = d["dev_tool"]["module"]["name"]
    SRC_DIR = realpath_join(HERE, "../", d["dev_tool"]["module"]["src_dir"], MODULE_NAME)
    if not path_exists(SRC_DIR):
        raise OSError(('Module source directory does not exist: "%s"') % SRC_DIR)
    main()