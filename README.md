![](image.jpg)

This is a little program to ease the selection of the next video to watch.

You configure it to start browsing on a main video directory. With rofi you navigate to subdirectories, clearly seeing which files have been played already.

---

Install [rofi](https://github.com/davatorium/rofi) to display the interface.

Run nextwatch and navigate to a file.

Watched files will have `[W]` at the start of the name.

Press enter to launch the file with a video player.

---

## Config

The config file is located at:

`~/.config/nextwatch/config.json`

This is created on first launch if not existent.

You likely will need to edit it.

`path`: The path to the main video directory.

`player`: The name of the video player.

`auto_watch`: Auto-mark selected files as watched.

`auto_dir`: Enter a directory automatically if it's the only option.

`auto_filter`: Filter out watched files automatically.

`watched_icon`: The icon to use on watched files.

`arrow_select`: Play videos when using Right arrow as well.

## Actions

`[!] Filter` to filter out watched files.

`[!] All` to show all files.

## Shortcuts

`Alt + 1` to toggle `Watched` on files.

## Watched

A file is determined to be watched if you select it through this interface.

Or if you mark it as watched manually with the shortcut.

When you select a file it is added to:

`~/.config/nextwatch/watched.json`

## Ignore Dirs

Every dir is checked recursively for the existence of a video file.

If a dir doesn't contain a video file it is not shown.

## Arguments

You can override the `path` config by sending a path as the argument:

`nextwatch "/path/to/some/videos"`

## Desktop File

There's an example desktop file you can use.

Edit it first, then do:

`cp nextwatch.desktop ~/.local/share/applications/.`

So you can launch it easily.