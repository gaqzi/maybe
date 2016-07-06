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
        return map(lambda x: x.path, self._results)

    def __bool__(self):
        return self.success

    def __nonzero__(self):
        return self.__bool__()


class Command(object):
    executioner = None

    def __init__(self, name, mapping):
        self.name = name
        self.mapping = mapping

    def run(self, paths):
        """

        Args:
            paths (list[Path]): A list of paths to run this command against

        Returns:
            CommandResults: The result of running this command
        """
        result = CommandResults()
        for path in paths:
            result.add(self.executioner.run(path, self._get_command(path)))

        return result

    def _get_command(self, path):
        return self.mapping.get(str(path)) or self._default_command()

    def _default_command(self):
        return self.mapping.get('default')

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __hash__(self):
        return hash(frozenset(self.__dict__))
