# My dev tool for MicroPython project
A simple CLI for MicroPython project

```
> python -m dev_tool --help
```

## Feature
- Use **pyproject.toml** to configure (`toml` module)
- Provide functions for downloading script file from GitHub (GitHub API & `requests`, `base64` module)
- download libs from [`micropython-lib`](https://github.com/micropython/micropython-lib)
- Add or update module dependencies from git submodule
- Compile module source to mpy (use independent [`mpy-cross`](https://pypi.org/project/mpy-cross/) module)
- Interaction with MicroPython boards (base on official `pyboard.py`)

## Get it
Just execute `get_dev_tool.py` in your project, it would download `dev_tool` into the project.
```
> curl https://raw.githubusercontent.com/ShenTengTu/mpy-dev-tool/master/get_dev_tool.py | sudo python3 -
```

Then use the command below to initialize `dev_tool`, it would create a default `pyproject.toml`:
```
> python -m dev_tool init
``` 

## Directory Structure
```
─ your_project
  └─ assets
  └─ dev_tool
  └─ dist
      └─ mpy 
  └─ ext_lib
  └─ lib
  └─ submodules
  └─ pyproject.toml
```
- **assets** : Place the files (like `*.json`, `*.jpg` etc.) used by main module to here.
- **dev_tool** : `dev_tool` CLI module.
- **dist** : Your project distribution is here.
  - **mpy** : All compiled `.py` file is here.
- **ext_lib** : All downloaded libs from `micropython-lib` is here. They would be installed in `/lib` directory on the board.
- **lib** : 3rd party MicroPython Lib is here. They would be installed in `/lib` directory on the board.
- **submodules** : Submodules from Git that the main module need to dependent (intent to package them into main module).
- **pyproject.toml** :`dev_tool` configuration is in this file.


