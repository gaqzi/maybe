from __future__ import unicode_literals

import os

import git


class DiffError(BaseException):
    def __init__(self, message, original):
        self.message = message
        self.original = original


class DifferBase(object):
    def __init__(self, base_path='.'):
        self._base_path = None
        self.base_path = base_path

    @property
    def base_path(self):
        return self._base_path

    @base_path.setter
    def base_path(self, value):
        self._base_path = os.path.abspath(value)

    def changed_files_between(self, from_commit, to_commit=None):
        raise NotImplementedError('changed_files_between is not implemented.')


class Git(DifferBase):
    DiffError = DiffError
    _repo = None

    @property
    def repo(self):
        if not self._repo:
            self._repo = git.Repo(self.base_path)
        return self._repo

    def changed_files_between(self, from_commit, to_commit=None):
        """Returns a list of changed files between two commits.

        Args:
            from_commit (str): A git commit reference
            to_commit (Union[str, None}): A git commit reference,
                default: None

        Returns:
            list[str]: The files that changed between
                the passed in commits
        """
        try:
            return self._list_of_files(
                self.repo.git.diff(from_commit, to_commit, name_only=True)
            )
        except git.exc.GitCommandError as exc:
            raise DiffError(
                "Failed to get list of changed files between '{0}' and {1}'".format(
                    from_commit,
                    to_commit or 'HEAD'
                ),
                exc
            )

    def _list_of_files(self, files):
        return filter(lambda x: x, files.strip().split('\n'))
