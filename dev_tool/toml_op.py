import toml


def write_toml(path, d):
    with open(path, mode="w") as f:
        toml.dump(d, f)


def read_toml(path):
    with open(path, mode="r") as f:
        d = toml.load(f)
    return d
