from __future__ import unicode_literals

import os

from maybe.executioners import ExecutionResults
from maybe import differs, executioners
from maybe import match
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
