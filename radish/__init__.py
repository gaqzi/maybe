from __future__ import unicode_literals

import glob
import itertools

import six
import yaml
from radish.command import Command
from radish.executioners import Executioner, ExecutionResult, ExecutionResults
from radish.path import Path

__version__ = '0.1.0'


def match(lines, paths):
    """

    Args:
        lines (list[Union[str, unicode]]): the files that has changed between the two commits
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
    if isinstance(conf_file, six.string_types):
        with open(conf_file, 'r') as fh:
            config = yaml.load(fh)
    else:
        config = yaml.load(conf_file)

    def expand_glob(path):
        if '*' in path:
            return [p for p in glob.glob(path)]
        else:
            return [path]

    paths = [expand_glob(path) for path in config['paths']]
    config['paths'] = [Path(path) for path in itertools.chain(*paths)]

    config['commands'] = {Command(name, mapping)
                          for name, mapping in config.get('commands', {}).items()}

    return config
