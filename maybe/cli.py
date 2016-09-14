from __future__ import unicode_literals, print_function

import os
import sys

from docopt import docopt

import maybe
from maybe import differs, executioners
from maybe import match
from maybe.executioners import ExecutionResults
from maybe.outputter import Outputter


class CLI(object):
    results = None

    def __init__(self, base_path='.', config=None, executioner=None, differ=None, outputter=None):
        self.outputter = outputter or Outputter()
        self.base_dir = os.path.abspath(base_path)
        self.executioner = executioner or executioners.Executioner(base_path=self.base_dir,
                                                                   outputter=outputter)
        self.config = config
        self.differ = differ or differs.Git(base_path)
        self.results = ExecutionResults()

    def run(self, command_name, paths):
        command = next((c for c in self.config['commands'] if c.name == command_name), None)

        for path, cmd in command.items(filter=paths):
            if cmd is None:
                continue

            self.outputter.info.write('Running {0} for {1}:\n'.format(command_name, path))

            self.results.add(self.executioner.run(path, cmd))

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

    raise Exception('No "Maybefile" available')


def main():
    """Maybe run a command if something has changed in a folder

    Usage:
      maybe command <command> [--from=<from_commit> [--to=<to_commit>]]
      maybe (-h | --help)
      maybe --version

    Options:
      --from=<from_commit>  The commit or reference to compare from
      --to=<to_commit>      The commit or reference to compare to
      -h --help             Show this screen
      --version             Show version
    """
    arguments = docopt(main.__doc__, version='maybe {0}'.format(maybe.__version__))

    cli = CLI(config=maybe.read_config(get_config_file('Maybefile', 'Maybefile.yml')))

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
