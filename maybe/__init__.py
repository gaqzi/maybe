from __future__ import unicode_literals

import yaml

from maybe.command import CommandResult, CommandResults, Command
from maybe.executioners import Executioner
from maybe.path import Path

__version__ = '0.1.0'


def match(lines, paths):
    """

    Args:
        lines (list[str]): the files that has changed between the two commits
        paths: (list[Path]): the configured paths we support

    Returns:
        set[Path]: The matched paths
    """
    matches = set()
    for line in lines:
        for path in paths:
            matches.add(path.match(line))

    return {x for x in matches if x}


def read_config(conf_file):
    """

    Args:
        conf_file (Union(TextIO, str)): A file pointer to read a config
            file from or a path to a file

    Returns:
        dict: A configuration dictionary
    """
    config = yaml.load(conf_file)
    config['paths'] = [Path(path) for path in config['paths']]

    config['commands'] = {Command(name, mapping) for name, mapping in config.get('commands', {}).items()}

    return config
