from __future__ import unicode_literals

import os

from maybe import differs, executioners
from maybe import match


class CLI(object):
    results = None

    def __init__(self, base_path='.', config=None, executioner=None, differ=None):
        self.base_dir = os.path.abspath(base_path)
        self.executioner = executioner or executioners.Executioner(base_path=self.base_dir)
        self.config = config
        self.differ = differ or differs.Git(base_path)

    def run(self, command, paths):
        cmd = next((c for c in self.config['commands'] if c.name == command),
                   None)  # type: Command
        self.results = cmd.run(paths, self.executioner)

        # for path in self._matched_paths(paths):
        #     command = self._command_for(path=path, command=command)
        #     path = os.path.join(self.base_dir, path)
        #
        #     self.results.add(command.run([path], self.executioner)._results[0])
        #
        return self.results

    def successful(self):
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

    def _matched_paths(self, paths):
        return set(self.config['paths']) if not paths else match(paths, self.config['paths'])

    def _command_for(self, path, command):
        # type: (Union[Path, str], str) -> Command
        for cmd in filter(lambda x: x.name == command, self.config['commands']):
            if str(path) in cmd.mapping:
                return cmd

        raise KeyError('No command "{0}" found for path "{1}"'.format(command, path))

    def _default_command(self):
        return self.config['commands'].get('default')

    def _join_base_dir_to_paths(self, paths):
        return map(lambda p: os.path.join(self.base_dir, p), paths)
