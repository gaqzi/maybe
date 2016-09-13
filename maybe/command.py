from __future__ import unicode_literals

from fnmatch import fnmatch


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
