from io import StringIO

import pytest

import maybe
from maybe import Path
from maybe.cli import CLI
from maybe.executioners import NullExecutioner
from maybe.outputter import Outputter


@pytest.fixture
def outputter():
    return Outputter(StringIO(), StringIO())


@pytest.fixture
def config():
    return dict(
        paths=[Path('extensions/rules/'), Path('js/frontend/'), Path('js/mobile/')],
        commands={maybe.Command('test', {
            'extensions/rules/': 'py.test',
            'js/*/': 'npm test'
        })}
    )


@pytest.fixture
def executioner(outputter):
    return NullExecutioner(0, outputter=outputter)


@pytest.fixture
def cli(config, outputter, executioner):
    return CLI(
        base_path='tests/support/dummy/',
        config=config,
        executioner=executioner,
        outputter=outputter,
    )


class TestCli(object):
    FIRST_GREEN_COMMIT = '10aac02e05'
    FIRST_GREEN_COMMIT_PY = '39e0889d06'

    def test_changed_projects_returns_all_configured_paths_with_no_commits_given(self, cli):
        assert cli.changed_projects() == {'extensions/rules/', 'js/frontend/', 'js/mobile/'}

    def test_changed_projects_returns_only_the_ones_with_changed_files(self, cli):
        assert cli.changed_projects(
            from_commit=self.FIRST_GREEN_COMMIT,
            to_commit=self.FIRST_GREEN_COMMIT_PY
        ) == {'extensions/rules/'}

    def test_will_run_the_passed_in_command_for_all_configured_folders(self, cli):
        paths = list(cli.changed_projects())

        cli.run('test', paths)

        assert cli.successful

    def test_executing_command_outputs_info_about_what_is_running_and_where(self, cli):
        cli.run('test', ['extensions/rules/'])

        out = cli.outputter.info.streams[0].getvalue()
        assert out == 'Running test for extensions/rules/:\n\n'
