from __future__ import unicode_literals

import os


class Path(object):
    GLOB_CHARACTER = '*'

    def __init__(self, path):
        """

        Args:
            path (Union(str, None)): A path to perform matches against
        """
        self.path = path

    def match(self, filename):
        """

        Args:
            filename (Union(str, Path)): A path in the repository that we're matching against

        Returns:
            Path: A path object that correlates to the matched file.
              If there isn't a match returns a :class:`Path` with the
              value ``None``.
        """
        if hasattr(filename, 'path'):
            return self.match(filename.path)
        elif filename.startswith(self.path):
            return self
        elif self.GLOB_CHARACTER in self.path:
            return Path(self._match_glob(filename))

        return Path(None)

    def _match_glob(self, filename):
        index = self.path.find(self.GLOB_CHARACTER)
        basepath = self.path[0:index]

        if filename.startswith(basepath):
            file_base_removed = filename.replace(basepath, '', 1)

            if '/' in file_base_removed:
                return os.path.join(
                    basepath,
                    file_base_removed.split('/', 1)[0],
                    ''  # Required to add a slash at the end
                )

        return None

    def __eq__(self, other):
        if other:
            if self.path == str(other):
                return True
            elif hasattr(other, 'path'):
                if self.GLOB_CHARACTER in self.path:
                    return self._match_glob(other.path)
                elif self.GLOB_CHARACTER in other.path:
                    return other == self
        elif bool(self) == bool(other):
            return True

        return False

    def __hash__(self):
        return hash(self.path)

    def __str__(self):
        return self.path or ''

    def __repr__(self):
        return '<Path: {0}>'.format(self or '<None>')

    def __bool__(self):
        return bool(self.path)

    def __nonzero__(self):
        return self.__bool__()

    def startswith(self, needle):
        return self.path.startswith(needle)

    def __add__(self, other):
        return '{0}{1}'.format(self.path, other)

    def __radd__(self, other):
        return '{0}{1}'.format(other, self.path)
