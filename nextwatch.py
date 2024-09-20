nimport json
import tomllib
from glob import glob
from subprocess import Popen, PIPE
from pathlib import Path


config = {}
config_path = Path("~/.config/nextwatch/config.toml").expanduser()

watched = []
watched_path = Path("~/.config/nextwatch/watched.json").expanduser()

allowed = [
    "mp4",
    "webm",
    "avi",
    "m4v",
    "mpeg",
    "flv",
    "mov",
    "mkv",
    "wmv",
    "vob",
    "ogv",
]


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
        try:
            watched = json.load(f)
        except:
            watched = []


def save_watched():
    with watched_path.open("w") as f:
        json.dump(watched, f)


def toggle_watched(path, name, index):
    global watched

    if name in watched:
        watched.remove(name)
    else:
        watched.append(name)

    save_watched()
    show_paths(path, selected=index)


def clean_watched(name):
    if name.startswith("[W] "):
        name = name[4:]

    return name.strip()


def show_paths(path, filter_watched=False, selected=0):
    allfiles = glob(f"{str(path)}/*")
    onlydirs = [f for f in allfiles if (path / Path(f)).is_dir()]
    onlyfiles = [f for f in allfiles if (path / Path(f)).is_file()]
    onlydirs.sort(key=lambda x: Path(x).name)
    onlyfiles.sort(key=lambda x: Path(x).name)

    files = []

    for f in onlyfiles:
        if Path(f).suffix[1:].lower() in allowed:
            files.append(f)

    items = []

    if str(path) != "/":
        items.append("..")

    if len(files) > 0:
        if filter_watched:
            items.append("[!] All")
        else:
            items.append("[!] Filter")

    for d in onlydirs:
        items.append(f"[+] {Path(d).name}")

    for f in files:
        name = f"{Path(f).name}"

        if name in watched:
            if filter_watched:
                continue

            name = f"[W] {name}"

        items.append(name)

    info = "Alt+1 = Toggle Watched"

    proc = Popen(
        f"rofi -dmenu -i -format i -inputchange-action 'kb-row-first' keys -kb-accept-alt '' -p '{info}' -selected-row {selected}",
        stdout=PIPE,
        stdin=PIPE,
        shell=True,
        text=True,
    )

    index, stderr = proc.communicate("\n".join(items))
    code = proc.returncode

    if code == 1:
        exit(0)

    ans = items[int(index)].strip()

    if ans == "":
        exit(0)

    if ans == "..":
        show_paths(Path(path).parent)
    elif ans.startswith("/") or ans.startswith("~"):
        show_paths(Path(ans).expanduser())
    elif ans.startswith("[+] "):
        show_paths(Path(path) / ans[4:])
    elif ans.startswith("[!] "):
        action = ans[4:]

        if action == "Filter":
            show_paths(path, True)
        elif action == "All":
            show_paths(path)
    else:
        ans = clean_watched(ans)

        if code == 10:
            toggle_watched(path, ans, index)
            return

        Popen([config["player"], str(path / ans)])

        with watched_path.open("r") as f:
            if ans not in watched:
                watched.append(ans)

            save_watched()


if __name__ == "__main__":
    read_config()
    read_watched()
    show_paths(Path(config["path"]))
