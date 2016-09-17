from __future__ import unicode_literals

import os

import pytest

from radish.differs import DifferBase, Git


class TestDifferBase(object):
    def test_set_base_path_to_non_absolute_makes_it_absolute_from_cwd(self):
        assert DifferBase(
            base_path='tests/support/dummy/'
        ).base_path == os.path.join(os.getcwd(), 'tests/', 'support/', 'dummy')


class TestGit(object):
    FIRST_GREEN_COMMIT = '10aac02e05'
    FIRST_GREEN_COMMIT_PY = '39e0889d06'

    def _differ(self):
        return Git(base_path='tests/support/dummy/')

    def test_git_returns_changed_files_between_two_commits(self):
        assert list(self._differ().changed_files_between(
            self.FIRST_GREEN_COMMIT,
            self.FIRST_GREEN_COMMIT_PY
        )) == [
            'extensions/roles_and_permissions/tests/test.py',
            'extensions/roles_and_permissions/tests/test_truth.py',
            'extensions/rules/tests/test.py',
            'extensions/rules/tests/test_truth.py',
            'js/.gitignore'
        ]

    def test_no_changes_returns_empty_list(self):
        assert list(self._differ().changed_files_between(self.FIRST_GREEN_COMMIT,
                                                         self.FIRST_GREEN_COMMIT)) == []

    def test_invalid_commit_ref_raises_exception(self):
        message = "Failed to get list of changed files between 'INVALID_REF' and 'HEAD'"
        with pytest.raises(Git.DiffError, message=message) as exc:
            self._differ().changed_files_between('INVALID_REF')

        assert exc.value.original
