Dev tool
========
.. code-block::

    python -m dev_tool [-h] task_commad

Task Commands
-------------
`download_ext_libs`
    download extra libraries to local from `micropython-lib`.

`add_submodule <submodule>`
    add a submodule into main module .

    `<submodule>`
        relative path of the submodule src directory in `submodules` folder.

`update_submodule <submodule_name>`
    update a submodule in main module .

    `<submodule_name>`
        submodule name in  main module folder.
`make_mpy`
    compile source `*.py` to `*.mpy` (save in *dist/mpy* folder).
`update_script`
    update the script file by github API (see pyproject.toml).
`pyboard_ls`
    pyboard: list the dir
`pyboard_install`
    pyboard: install mpy distribution to the board

About update script
-------------------
If the script file no exist:

- From gist: Specify `file`, `gist_id` fields,
  use `--ref` argument to to specify gist version (sha).
- From repo content: Specify `file`, `owner`, `repo`, `path` fields,
  use `--ref` argument to to specify the repo reference.

If the script file has been exist:

- From gist: Auto upate to the lastest revision.
- From repo content: Use `--ref` argument to to specify the reference.

You can use `--toml` to specify config toml file (the path base on CWD).

.. code-block::

    python -m dev_tool update_script --dev repo_contents pyboard.py -ref v1.12 --toml ./dev_tool/script_src.toml


About Interaction with PyBoard
------------------------------
The prefix of the PyBoard Interaction Commands  is `pyboard_` or `py_`.

PyBoard arguments:

`--port`
    the serial device or the IP address of the pyboard
`-baud`
    the baud rate of the serial device
`--user`
    the telnet login username
`--password`
    the telnet login password
`--wait`
    seconds to wait for USB connected board to become available
`--delay`
    seconds to wait before entering raw REPL

.. code-block::

    python -m dev_tool -p com14 pyb_ls

