import os
import json
import sys
from glob import glob
from glob import escape
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

indices = {}

root_path = ""


def read_config():
    global config

    if not config_path.exists():
        with config_path.open("w") as f:
            f.write("{}")

    with config_path.open("r") as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError:
            init_config()

    if "path" not in config:
        init_config()
    elif check_config():
        save_config()


def init_config():
    global config

    config = {
        "path": "~/videos",
    }

    check_config()
    save_config()


def check_config():
    changed = False

    if not config["path"].endswith("/"):
        config["path"] += "/"
        changed = True

    if "player" not in config:
        config["player"] = "haruna"
        changed = True

    if "auto_watch" not in config:
        config["auto_watch"] = True
        changed = True

    if "auto_dir" not in config:
        config["auto_dir"] = True
        changed = True

    if "auto_filter" not in config:
        config["auto_filter"] = False
        changed = True

    if "watched_icon" not in config:
        config["watched_icon"] = "[W]"
        changed = True

    if "arrow_select" not in config:
        config["arrow_select"] = False
        changed = True

    if "ignore_dirs" not in config:
        config["ignore_dirs"] = True
        changed = True

    return changed


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
        except json.JSONDecodeError:
            watched = []
            save_watched()


def save_watched():
    with watched_path.open("w") as f:
        json.dump(watched, f)


def toggle_watched(path, name, mode):
    global watched

    if name in watched:
        watched.remove(name)
    else:
        watched.append(name)

    save_watched()
    show_paths(path, mode=mode)


def set_watched(name):
    if name not in watched:
        watched.append(name)
        save_watched()


def clean_name(name):
    icon = config["watched_icon"]

    if name.startswith(f"{icon} "):
        name = name[len(icon) + 1 :]

    return name.strip()


def play_video(path):
    Popen([config["player"], path])


def at_root(path):
    return path == root_path


def show_paths(path, mode="normal", direction="forwards"):
    if not path.endswith("/"):
        path += "/"

    if path in indices:
        selected = indices[path]
    else:
        selected = 0

    if mode == "normal":
        if config["auto_filter"]:
            filter_watched = True
        else:
            filter_watched = False
    elif mode == "watched":
        filter_watched = True
    elif mode == "all":
        filter_watched = False

    ppath = Path(path)
    allfiles = glob(f"{escape(path)}*")
    onlydirs = [f for f in allfiles if (ppath / Path(f)).is_dir()]
    dirs = []

    if config["ignore_dirs"]:
        for d in onlydirs:
            all_d_files = glob(os.path.join(escape(d), "**", "*"), recursive=True)

            for f in all_d_files:
                ext = Path(f).suffix[1:].lower()

                if ext in allowed:
                    dirs.append(d)
                    break
    else:
        dirs = onlydirs

    onlyfiles = [f for f in allfiles if (ppath / Path(f)).is_file()]
    dirs.sort(key=lambda x: Path(x).name)
    onlyfiles.sort(key=lambda x: Path(x).name)
    files = []

    for f in onlyfiles:
        if Path(f).suffix[1:].lower() in allowed:
            files.append(f)

    if (len(files) == 0) and (len(dirs) == 1):
        if config["auto_dir"]:
            if direction == "forwards":
                show_paths(dirs[0])
                return
            elif direction == "back":
                if not at_root(path):
                    indices[path] = 0
                    show_paths(str(ppath.parent), direction="back")

                return

    items = []
    items.append("..")

    if len(files) > 0:
        if filter_watched:
            items.append("[!] All")
        else:
            items.append("[!] Filter")

    for d in dirs:
        items.append(f"[+] {Path(d).name}")

    icon = config["watched_icon"]

    for f in files:
        name = f"{Path(f).name}"

        if name in watched:
            if filter_watched:
                continue

            name = f"{icon} {name}"

        items.append(name)

    info = "Alt+1 = Toggle Watched"

    rofi_cmd = f"""
    rofi -dmenu -i -format i
    -inputchange-action 'kb-row-first'
    keys -kb-accept-alt ''
    -kb-move-char-back ''
    -kb-move-char-forward ''
    -kb-custom-11 'Left'
    -kb-custom-12 'Right'
    -p '{info}'
    -selected-row {selected}
    """

    rofi_cmd = " ".join(rofi_cmd.strip().split())

    proc = Popen(
        rofi_cmd,
        stdout=PIPE,
        stdin=PIPE,
        shell=True,
        text=True,
    )

    s_index, stderr = proc.communicate("\n".join(items))
    code = proc.returncode

    if code == 1:
        exit(0)

    index = int(s_index)
    ans = items[index].strip()

    if ans == "":
        exit(0)

    indices[path] = index

    if ans == ".." or (code == 20):
        if not at_root(path):
            indices[path] = 0
            show_paths(str(ppath.parent), direction="back")
        else:
            show_paths(path)
    elif ans.startswith("/") or ans.startswith("~"):
        show_paths(str(Path(ans).expanduser()))
    elif ans.startswith("[+] "):
        show_paths(str(ppath / ans[4:]))
    elif ans.startswith("[!] "):
        action = ans[4:]

        if action == "Filter":
            show_paths(path, mode="watched")
        elif action == "All":
            show_paths(path, mode="all")
    else:
        if code == 21:
            if not config["arrow_select"]:
                show_paths(path)
                return

        name = clean_name(ans)

        if code == 10:
            toggle_watched(path, name, mode)
            return

        play_video(str(ppath / name))

        if config["auto_watch"]:
            set_watched(name)


def main():
    global root_path

    read_config()

    if len(sys.argv) > 1:
        root_path = sys.argv[1]
    else:
        root_path = config["path"]

    if not root_path.endswith("/"):
        root_path += "/"

    read_watched()
    show_paths(root_path)


if __name__ == "__main__":
    main()
