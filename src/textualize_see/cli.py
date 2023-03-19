from __future__ import annotations

import click
import shlex
import os
import sys

from .errors import AppError
from .file_map import FileMap


@click.command(
    context_settings={
        "ignore_unknown_options": True,
    },
)
@click.option(
    "-c",
    "--config",
    default=lambda: os.environ.get("SEE_CONFIG", "~/.see.toml"),
    help="Location of configuration file",
)
@click.option("-n", "--no-run", is_flag=True, help="Display command but don't run it.")
@click.argument(
    "path",
    metavar="[ACTION] PATH",
)
@click.argument(
    "forward_args", nargs=-1, type=click.UNPROCESSED, metavar="<ARG1, ARG2, ...>"
)
def app(config: str, no_run: bool, path: str, forward_args: list[str]) -> None:
    """Open files in the terminal."""

    action = "view"
    if "." not in path and forward_args:
        action = path
        path = forward_args[0]
        forward_args = forward_args[1:]

    try:
        file_map = FileMap(config)
    except AppError as app_error:
        print(str(app_error), file=sys.__stderr__)
        sys.exit(1)

    args = shlex.join(forward_args)

    for command in file_map.get_commands(path, action):
        run = command.run.replace("$ARGS", args).replace("$PATH", shlex.quote(path))
        if no_run:
            print(run)
        else:
            sys.exit(os.system(run))
        break
    print("No matching pattern in `~/.see.toml`", file=sys.stderr)
    sys.exit(1)
