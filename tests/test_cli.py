import maybe
from maybe import Path
from maybe.cli import CLI
from maybe.executioners import NullExecutioner


class TestCli(object):
    config = dict(
        paths=[Path('extensions/rules/'), Path('js/frontend/'), Path('js/mobile/')],
        commands={maybe.Command('test', {
            'extensions/rules/': 'py.test',
            'js/*/': 'npm test'
        })}
    )
    FIRST_GREEN_COMMIT = '10aac02e05'
    FIRST_GREEN_COMMIT_PY = '39e0889d06'

    def test_changed_projects_returns_all_configured_paths_with_no_commits_given(self):
        cli = CLI(base_path='tests/support/dummy/', config=self.config)

        assert cli.changed_projects() == {'extensions/rules/', 'js/frontend/', 'js/mobile/'}

    def test_changed_projects_returns_only_the_ones_with_changed_files(self):
        cli = CLI(base_path='tests/support/dummy/', config=self.config)

        assert cli.changed_projects(
            from_commit=self.FIRST_GREEN_COMMIT,
            to_commit=self.FIRST_GREEN_COMMIT_PY
        ) == {'extensions/rules/'}

    def test_will_run_the_passed_in_command_for_all_configured_folders(self):
        cli = CLI(
            base_path='tests/support/dummy/',
            config=self.config,
            executioner=NullExecutioner(0)
        )
        cli.run('test', cli.changed_projects())

        assert cli.successful
