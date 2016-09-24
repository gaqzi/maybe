from __future__ import unicode_literals, print_function

import glob
import itertools
import os

import six
import yaml
from docopt import docopt

import radish
from radish import differs
from radish import splitter
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
        if isinstance(command_name, Command):
            command = command_name
        else:
            command = self.find_command(command_name)

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

    def find_command(self, command_name):
        return next((c for c in self.config['commands'] if c.name == command_name), None)


def get_config_file(*filenames):
    for filename in filenames:
        if os.path.exists(filename):
            return os.path.abspath(filename)

    raise OSError('No file "{0}" found'.format(', '.join(filenames)))


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


class RadishExit(SystemExit):
    def __init__(self, message_or_code):
        super(RadishExit, self).__init__(message_or_code)


def main(args=None):
    """radish a task runner that understands version control

Usage:
  radish command <command> [--from=<from_commit> [--to=<to_commit>]]
                           [--jobs=<jobs> [--job=<job_index>]]
  radish (-h | --help)
  radish --version

  --from=<from_commit>         The commit or reference to compare from
  --to=<to_commit>             The commit or reference to compare to
  -j <jobs>, --jobs=<jobs>     The number of parallel jobs to run
  -J <job_index>, --job=<job_index>  The index of the current job to run, will
                               consistently map jobs to run to this index.
  -h, --help                   Show this screen
  --version                    Show version
    """
    arguments = docopt(
        six.text_type(main.__doc__),
        version='radish {0}'.format(radish.__version__),
        argv=args
    )

    cli = CLI(
        config=read_config(get_config_file('Radishfile', 'Radishfile.yml'))
    )

    command = cli.find_command(arguments['<command>'])
    if not command:
        raise RadishExit(
            'No command "{0}" registered.\n\nAvailable commands:\n\t{1}'.format(
                arguments['<command>'],
                '\n\t'.join(map(lambda cmd: cmd.name, cli.config['commands']))
            )
        )

    changed_projects = splitter.split(
        cli.changed_projects(
            from_commit=arguments['--from'],
            to_commit=arguments['--to'],
        ),
        splits=arguments['--jobs'],
        index=arguments['--job']
    )

    if arguments['--jobs']:
        if arguments['--job']:
            no_jobs = 'as job {}/{}'.format(
                int(arguments['--job']) + 1,
                arguments['--jobs']
            )
        else:
            no_jobs = 'with {} processes'.format(arguments['--jobs'])

        cli.outputter.info.write('Running commmand {} in parallel {}\n\n'.format(
            command.name,
            no_jobs
        ))

    cli.outputter.info.write('Changed paths:\n')
    for project in changed_projects:
        cli.outputter.info.write('\t{0}\n'.format(project))
    cli.outputter.info.write('\n')

    results = cli.run(
        command_name=command,
        paths=changed_projects,
    )

    for result in results:
        cli.outputter.info.write(
            '{}: {} ({})\n'.format(
                result.path,
                'Success' if result.success else 'Failure',
                result.run_time
            )
        )
    cli.outputter.info.write('\n')
    cli.outputter.info.write('Commands finished in {}\n'.format(results.run_time))

    raise RadishExit(0 if results else 10)
