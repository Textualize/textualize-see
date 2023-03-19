# Textualize See

Textualize See is a command line tool to open files in the terminal.

A TOML configuration file maps glob-style patterns on to commands. You could configure `see` to open any file matching the pattern "*.py*" with [rich-cli](https://github.com/Textualize/rich-cli) and "*.rs" files with [bat](https://github.com/sharkdp/bat), for example.

Think of `see` as the terminal equivalent of double-clicking a file on the desktop.

The configuration is flexible enough that `see` can run a different command depending on the directory. For instance you might want to a different command to display `.html` files (in reality, template files) in a Django project.

While the default is to *view* the file, you can also request different actions, such as "edit", "format", "print" etc. 

## Install

`See` is distributed as a Python package.
The easiest way to install it is probably with [pipx](https://pypa.github.io/pipx/).

```
pipx textualize_see
```

This will add `see` to your path.

## Usage

> **Note**
> You will need to configure `see` before you use it.

Call `see` with a path to view that file in the terminal:

```
see application.py
```

If you add two arguments, then the first should be an *action*, and the second should be a path.

```
see edit application.py
```

This will open `application.py` with a command to edit the file.

Any additional arguments added after the path are forwarded to the command.
In the following `--pager` is not an option for `see`, so it will be forwarded to the command that opens the file.

```
see application.py --pager
```

Note that `see` will run commands for configured paths only.
If there is no matching path then `see` will do nothing.
See below for configuration.

## Configure

Textual reads its configuration from `~/.see.toml` (a [TOML](https://toml.io/en/) file).
This file should consist of several tables which specify the action (e.g. "view") and a glob style pattern to match against.

The table should have a `run` key which defines the command to run.
The `run` value may contain `$PATH` or `$ARGS` which will be replaced with the path and forward arguments respectively. 

The following will match any files with the extension ".py":

```toml
[[actions.view."*.py"]]
run = "rich $PATH $ARGS"
```

If you were to run the following `see` command:

```
see application.py --pager
```

Then `see` would pass the path to `rich` along with any options it doesn't recognize, such as `--pager`.

```
rich application.py --pager
```

### Priority

You can optionally add a `priority` integer value, associated with a pattern.
If not provided, `priority` will default to 1.

If more than one pattern matches the path, then the action with the highest priority will be used.
This can be used to add a fallback if there is no explicit match.
For example, we could add the following section to `cat` any files to the terminal that we haven't explicitly matched:

```toml
[[actions.view."*"]]
priority = 0
run = "cat $PATH $ARGS"
```

## Why did I build this?

I've always felt something like this should exist.
It is functionality that desktops take for granted, but the experience is not quite as transparent in the terminal.
There are alternatives (see below) but this is how I would want it work.
It is also cross-platform so I don't seem like a fish out of water on Windows.

## Why not just use ... ?

Inevitably this will prompt the question "Why not just use TOOL?".
I don't want to talk you out of TOOL, but this is what I considered:

### open or xdg-open

There is `open` on macOS, and `xdg-open` on Linux, which open files.
But these typically open desktop applications, and when I'm in the terminal I typically want to stay in the terminal.

### hash bangs?

The hash bang `#!` is used to *execute* the file, while I just want to open it. It also requires that you can edit the file itself.

### shell aliases

You could add an alias for each filetype you want to open, like `md-view` and `md-edit` etc.
Which is a perfectly reasonable use for alias, but it does require a command per filetype + action which is harder to commit to muscle memory.

ZSH offers `alias -s` which associates a file extension with a command.
For example if you have the alias `alias -s py=rich` then you can enter `foo.py` to syntax a Python file.
I like this, but I *think* it is only offered by the `zsh` shell (may be wrong) and it is not cross platform.

## Why Python?

It's Python because I am mainly a Python developer.
Tools like this do tend to be written a little closer to the metal.
If `see` becomes popular and the interface stabilizes, then maybe I (or somebody else) will write it a compiled language.
Until then you might have to wait an additional few microseconds to run apps.

## Support

Consider this project alpha software for the time being.
It was written in under a day and hasn't been battle tests.
It has so far only been tested under MacOS, but the goal is to make it work across all the platforms.
