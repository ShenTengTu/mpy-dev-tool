from .pyboard import Pyboard, PyboardError
import time
from re import search
from . import os_strerror, path_split


def pyb_parse_errno(err):
    traceback_str = str(err.args[-1].decode("utf-8"))
    os_err_msg = traceback_str.splitlines()[-1]
    m = search(r"Errno (?P<errno>\d+)", os_err_msg)
    code = int(m.group("errno"))
    return (code, os_strerror(code))


class _PyboardContext:
    def __init__(self, pyb: Pyboard, delay):
        self.__pyb = pyb
        self.delay = delay

    @property
    def pyb(self):
        return self.__pyb

    def __enter__(self):
        time.sleep(self.delay)
        self.pyb.enter_raw_repl()
        return self

    def __exit__(self, *exc):
        self.pyb.exit_raw_repl()
        self.pyb.close()

    def _mk_dir(self, dir_):
        try:
            self.pyb.fs_mkdir(dir_)
            return (0, None)
        except PyboardError as err:
            return pyb_parse_errno(err)

    def mk_dir(self, dir_, verbose=True):
        """
        Create a directory (prevent raising `EEXIST`)
        """
        err_no, err_msg = self._mk_dir(dir_)
        if err_no > 0:
            s = "[pyboard] %s (%s)" % (err_msg, dir_)
            if err_no == 17:  # EEXIST
                if verbose:
                    print(s)
            else:
                raise PyboardError(s)

    def mk_dirs(self, dir_):
        """
        Recursive directory creation (prevent raising `EEXIST`)
        """
        head, tail = path_split(dir_)
        if not tail:
            head, tail = path_split(head)
        if head and tail:
            self.mk_dirs(head)
        err_no, err_msg = self._mk_dir(dir_)
        if err_no > 0:
            if err_no not in (2, 17):  # ENOENT, EEXIST
                raise PyboardError("[pyboard] %s (%s)" % (err_msg, dir_))


class PyboardContextbuilder:
    """
    Invoke the instance as function to get a context manager of the Pyboard.

    Example:
    .. code-block:: python

        pyb_context_builder = PyboardContextbuilder("COM14")

        with pyb_context_builder(delay=3) as pyb_context:
        pyb_context.mk_dir("lib")
        pyb_context.ls()
    """

    def __init__(self, *args, **kwargs):
        self.__pyb = Pyboard(*args, **kwargs)

    def __call__(self, delay=3) -> _PyboardContext:
        """
        `delay` : A delay before enter raw REPL

        Return a context manager
        """
        return _PyboardContext(self.__pyb, delay)
