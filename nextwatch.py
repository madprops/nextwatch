import json
import tomllib
from glob import glob
from subprocess import Popen, PIPE
from pathlib import Path


config = {}
config_path = Path("~/.config/nextwatch/config.toml").expanduser()

watched = []
watched_path = Path("~/.config/nextwatch/watched.json").expanduser()


def read_config():
    global config

    with config_path.open("rb") as f:
        config = tomllib.load(f)


def read_watched():
    global watched

    if not watched_path.exists():
        with watched_path.open("w") as f:
            f.write("[]")

    with watched_path.open("r") as f:
        watched = json.load(f)


def show_paths(path):
    allfiles = glob(f"{str(path)}/*")
    onlydirs = [f for f in allfiles if (path / Path(f)).is_dir()]
    onlyfiles = [f for f in allfiles if (path / Path(f)).is_file()]
    onlydirs.sort(key=lambda x: Path(x).name)
    onlyfiles.sort(key=lambda x: Path(x).name)
    items = []

    if str(path) != "/":
        items.append("..")

    for d in onlydirs:
        items.append(f"[+] {Path(d).name}")

    for f in onlyfiles:
        name = f"{Path(f).name}"

        if name in watched:
            name = f"[W] {name}"

        items.append(name)

    proc = Popen(
        f"rofi -dmenu -i -p '{path}'", stdout=PIPE, stdin=PIPE, shell=True, text=True
    )

    ans = proc.communicate("\n".join(items))[0].strip()

    if ans == "":
        exit(0)

    ans = ans.strip()

    if ans == "..":
        show_paths(Path(path).parent)
    elif ans.startswith("/") or ans.startswith("~"):
        show_paths(Path(ans).expanduser())
    elif ans.startswith("[+] "):
        show_paths(Path(path) / ans[4:])
    else:
        if ans.startswith("[W] "):
            ans = ans[4:].strip()

        Popen(["haruna", str(path / ans)])

        with watched_path.open("r") as f:
            if ans not in watched:
                watched.append(ans)

            with watched_path.open("w") as f:
                json.dump(watched, f)


if __name__ == "__main__":
    read_config()
    read_watched()
    show_paths(Path(config["path"]))
