from __future__ import unicode_literals

from fnmatch import fnmatch


class CommandResult(object):
    def __init__(self, exit_code, run_time, path):
        self.exit_code = exit_code
        self.run_time = run_time
        self.path = path

    @property
    def success(self):
        return True if self.exit_code == 0 else False

    def __bool__(self):
        return self.success

    def __nonzero__(self):
        return self.__bool__()

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @classmethod
    def none(cls):
        """Returns a null object version of :class:`CommandResult`

        Returns:
            CommandResult: with all values set to 0 or None
        """
        return cls(0, 0, None)


class CommandResults(object):
    def __init__(self):
        self._results = []

    def add(self, result):
        """

        Args:
            result (CommandResult): The result of running a command for a given path
        """
        self._results.append(result)

    @property
    def success(self):
        if self._results:
            return all(self._results)
        else:
            return False

    @property
    def run_time(self):
        return sum(map(lambda x: x.run_time, self._results), 0.0)

    @property
    def paths(self):
        return [x.path for x in self._results if x.path is not None]

    def __bool__(self):
        return self.success

    def __nonzero__(self):
        return self.__bool__()


class Command(object):
    executioner = None

    def __init__(self, name, mapping):
        """

        Args:
            name (Union[str, unicode]): The name of this command
            mapping (Dict[maybe.Path, Command]): What commands to run at what paths.
                The key ``default`` is used when no match is found.
        """
        self.name = name
        self.mapping = mapping

    def run(self, paths, executioner=None, outputter=None):
        """

        Args:
            paths (list[Path]): A list of paths to run this command against
            executioner (maybe.BaseExecutioner): The executioner to run this command through

        Returns:
            CommandResults: The result of running this command
        """
        result = CommandResults()
        for path in paths:
            if outputter:
                outputter.info.write('Running {0} for {1}:'.format(self.name, path))

            result.add(executioner.run(path, self._get_command(path)))

            if outputter:
                outputter.info.write('\n')

        return result

    def items(self, filter=None):
        if filter:
            return [(path, self._get_command(path)) for path in filter]
        else:
            return self.mapping.items()

    def _get_command(self, path):
        return (self.mapping.get(str(path)) or
                self._glob_command(path) or
                self._default_command())

    def _default_command(self):
        return self.mapping.get('default')

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __hash__(self):
        return hash(frozenset(self.__dict__))

    def _glob_command(self, actual_path):
        for command_path, command in self.mapping.items():
            if fnmatch(str(actual_path), command_path):
                return command
