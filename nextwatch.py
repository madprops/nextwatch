import json
from glob import glob
from subprocess import Popen, PIPE
from pathlib import Path


config = {}
config_path = Path("~/.config/nextwatch/config.json").expanduser()

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

    if not config_path.exists():
        with config_path.open("w") as f:
            f.write("{}")

    with config_path.open("r") as f:
        try:
            config = json.load(f)
        except:
            init_config()

    if "path" not in config:
        init_config()


def init_config():
    global config

    config = {
        "path": "~/videos",
        "player": "haruna",
        "auto_watch": True,
        "auto_dir": True,
    }

    save_config()


def save_config():
    with config_path.open("w") as f:
        json.dump(config, f)


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
            save_watched()


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


def set_watched(name):
    if name not in watched:
        watched.append(name)
        save_watched()


def clean_name(name):
    if name.startswith("[W] "):
        name = name[4:]

    return name.strip()


def play_video(path):
    Popen([config["player"], path])


def show_paths(path, filter_watched=False, selected=0):
    ppath = Path(path)
    allfiles = glob(f"{path}/*")
    onlydirs = [f for f in allfiles if (ppath / Path(f)).is_dir()]
    onlyfiles = [f for f in allfiles if (ppath / Path(f)).is_file()]
    onlydirs.sort(key=lambda x: Path(x).name)
    onlyfiles.sort(key=lambda x: Path(x).name)

    files = []

    for f in onlyfiles:
        if Path(f).suffix[1:].lower() in allowed:
            files.append(f)

    if len(files) == 0:
        if len(onlydirs) == 1:
            if config["auto_dir"]:
                show_paths(Path(onlydirs[0]))
                return

    items = []

    if path != "/":
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
        show_paths(str(ppath.parent))
    elif ans.startswith("/") or ans.startswith("~"):
        show_paths(str(Path(ans).expanduser()))
    elif ans.startswith("[+] "):
        show_paths(str(ppath / ans[4:]))
    elif ans.startswith("[!] "):
        action = ans[4:]

        if action == "Filter":
            show_paths(path, True)
        elif action == "All":
            show_paths(path)
    else:
        name = clean_name(ans)

        if code == 10:
            toggle_watched(path, name, index)
            return

        play_video(str(ppath / name))

        if config["auto_watch"]:
            set_watched(name)


if __name__ == "__main__":
    read_config()
    read_watched()
    show_paths(config["path"])
