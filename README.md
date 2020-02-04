# My dev tool for MicroPython project
A simple CLI for MicroPython project

```
> python -m dev_tool --help
```

## Feature
- Use **pyproject.toml** to configure (`toml` module)
- Provide functions for downloading script file from GitHub (GitHub API & `requests`, `base64` module)
- Add or update module dependencies from git submodule
- Compile module source to mpy (use independent [`mpy-cross`](https://pypi.org/project/mpy-cross/) module)
- Interaction with MicroPython boards (base on official `pyboard.py`)

## Get it
Just execute `get_dev_tool.py` in your project, it would download `dev_tool` & `pyproject.toml` into the project.
```
> python get_dev_tool.py
```


