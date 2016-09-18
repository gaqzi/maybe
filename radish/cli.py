from __future__ import unicode_literals, print_function

import glob
import itertools
import os
import sys

import radish
import six
import yaml
from docopt import docopt
from radish import differs
from radish.command import Command
from radish.executor import Executor, ExecutionResults
from radish.outputter import Outputter
from radish.path import Path


class CLI(object):
    def __init__(self, base_path='.', config=None, executor=None, differ=None, outputter=None):
        self.base_dir = os.path.abspath(base_path)
        self.outputter = outputter or Outputter()
        self.executor = executor or Executor(base_path=self.base_dir, outputter=self.outputter)
        self.config = config
        self.differ = differ or differs.Git(self.base_dir)
        self.results = ExecutionResults()

    def run(self, command_name, paths):
        command = next((c for c in self.config['commands'] if c.name == command_name), None)

        for path, cmd in command.items(filter=paths):
            if cmd is None:
                continue

            self.outputter.info.write('Running {0} for {1}:\n'.format(command_name, path))

            self.results.add(self.executor.execute(path, cmd))

            self.outputter.info.write('\n')

        return self.results

    def changed_projects(self, from_commit=None, to_commit=None):
        if from_commit is None:
            return set(self.config['paths'])

        return match(
            self.differ.changed_files_between(
                from_commit=from_commit,
                to_commit=to_commit
            ),
            self.config['paths']
        )


def get_config_file(*filenames):
    for filename in filenames:
        if os.path.exists(filename):
            return os.path.abspath(filename)

    raise Exception('No "Radishfile" available')


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


def main():
    """radish a task runner that understands version control

    Usage:
      radish command <command> [--from=<from_commit> [--to=<to_commit>]]
      radish (-h | --help)
      radish --version

    Options:
      --from=<from_commit>  The commit or reference to compare from
      --to=<to_commit>      The commit or reference to compare to
      -h --help             Show this screen
      --version             Show version
    """
    arguments = docopt(six.text_type(main.__doc__), version='radish {0}'.format(radish.__version__))

    cli = CLI(config=read_config(get_config_file('Radishfile', 'Radishfile.yml')))

    if arguments['command'] or arguments['cmd']:
        changed_projects = cli.changed_projects(
            from_commit=arguments['--from'],
            to_commit=arguments['--to'],
        )

        print('Changed paths:')
        for project in changed_projects:
            print('\t{0}'.format(project))
        print()

        results = cli.run(
            command_name=arguments['<command>'],
            paths=changed_projects,
        )

        for result in results:
            print('{}: {} ({})'.format(result.path,
                                       'Success' if result.success else 'Failure',
                                       result.run_time))
        print()
        print('Commands finished in {}'.format(results.run_time))

        exit(0 if results else 1)
    else:
        print('I have no idea how we ended up here', file=sys.stderr)
        print(__doc__)
        exit(1)
