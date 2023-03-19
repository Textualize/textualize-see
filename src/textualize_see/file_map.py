from __future__ import annotations


from dataclasses import dataclass, field
from operator import attrgetter
from pathlib import Path

import toml
from toml.decoder import TomlDecodeError

from .errors import AppError


@dataclass
class Command:
    """A command to run with a file."""

    action: str = "view"
    run: str = ""
    priority: int = 1


@dataclass
class Config:
    paths: dict[str, list[Command]] = field(default_factory=dict)


class FileMap:
    """A map of files and extensions."""

    def __init__(self, path: str) -> None:
        """Initialise a file map.

        Args:
            path (str): Path ot the toml config
        """
        self.config = self._read_config(path)

    def get_commands(self, path: str, action: str) -> list[Command]:
        """Get commands associated with a path."""

        results: list[Command] = []
        for wildcard, commands in self.config.paths.items():
            if Path(path).resolve().match(wildcard):
                for command in commands:
                    if command.action == action:
                        results.append(command)
        results.sort(key=attrgetter("priority"), reverse=True)
        return results

    def _read_config(self, path: str) -> Config:
        """Ready TOML config.

        Args:
            path (str): Path to the config.

        Raises:
            AppError: If the config failed to load or validate.


        Returns:
            Config: Config object.
        """

        try:
            data = toml.load(Path(path).expanduser())
        except FileNotFoundError:
            raise AppError(f"Unable to read config {path!r}")
        except TomlDecodeError as error:
            raise AppError(f"Unable to parse TOML config {path!r}: {error}")

        config = Config()

        actions = data.get("actions", {})

        for action, action_commands in actions.items():
            for ext, extensions in action_commands.items():
                for extension_config in extensions:
                    run = extension_config.get("run", "")
                    if not isinstance(action, str):
                        raise AppError(
                            f"Config invalid: [[{action}.{ext}]] / 'action' expected string, found {run!r}"
                        )
                    if not run:
                        continue
                    priority = extension_config.get("priority", 1)
                    if not isinstance(priority, int):
                        raise AppError(
                            f"Config invalid: [[{action}.{ext}]] / 'priority' expected int, found {priority!r}"
                        )
                    extension = Command(action, run, priority)
                    config.paths.setdefault(ext, []).append(extension)

        return config
