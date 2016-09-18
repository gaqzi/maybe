from __future__ import unicode_literals

from io import StringIO

import radish.cli
from radish.command import Command
from radish.outputter import Outputter
from radish.path import Path


class TestCli(object):
    FIRST_GREEN_COMMIT = '10aac02e05'
    FIRST_GREEN_COMMIT_PY = '39e0889d06'

    class TestInit(object):
        def test_outputter_gets_instantiated_if_not_passed_in(self):
            cli = radish.cli.CLI(outputter=None)

            assert isinstance(cli.outputter, Outputter)

        def test_base_dir_is_converted_to_absolute_path(self):
            cli = radish.cli.CLI(base_path='.')

            assert cli.base_dir.startswith('/')

        def test_executor_gets_instantiated_with_base_dir_and_outputter(self):
            cli = radish.cli.CLI(executor=None)

            assert cli.executor.base_path == cli.base_dir
            assert cli.executor.outputter == cli.outputter

        def test_differ_gets_instantiated_with_base_dir(self):
            cli = radish.cli.CLI(differ=None, base_path='/tmp')

            assert cli.differ.base_path == cli.base_dir

    def test_changed_projects_returns_all_configured_paths_with_no_commits_given(self, cli):
        assert cli.changed_projects() == {'extensions/rules/', 'js/frontend/', 'js/mobile/'}

    def test_changed_projects_returns_only_the_ones_with_changed_files(self, cli):
        assert cli.changed_projects(
            from_commit=self.FIRST_GREEN_COMMIT,
            to_commit=self.FIRST_GREEN_COMMIT_PY
        ) == {'extensions/rules/'}

    def test_will_run_the_passed_in_command_for_all_configured_folders(self, cli):
        paths = list(cli.changed_projects())

        results = cli.run('test', paths)

        assert cli.results.success
        assert len(results.paths) == 3
        assert results.paths == paths

    def test_returns_empty_result_when_theres_no_matched_paths(self, cli):
        results = cli.run('test', ['error/'])

        assert not cli.results.success
        assert results.paths == []
        assert results.run_time == 0.0

        out = cli.outputter.info.streams[0].getvalue()
        assert out == ''

    def test_executing_command_outputs_info_about_what_is_running_and_where(self, cli):
        cli.run('test', ['extensions/rules/'])

        out = cli.outputter.info.streams[0].getvalue()
        assert out == 'Running test for extensions/rules/:\n\n'


class TestMatch(object):
    def test_returns_nothing_for_no_matches(self):
        lines = ['test/m000.py']
        paths = [Path('extensions/cool-extension')]

        assert radish.cli.match(lines, paths) == set()

    def test_returns_unique_matched_paths(self):
        lines = [
            'extensions/cool-extension/src/a.py',
            'extensions/cool-extension/tests/test_a.py'
        ]
        paths = [Path('extensions/cool-extension/')]

        assert radish.cli.match(lines, paths) == {'extensions/cool-extension/'}

    def test_returns_unique_matched_globbed_directories(self):
        lines = [
            'extensions/cool-extension/src/a.py',
            'extensions/warm-extension/src/b.py'
        ]
        paths = [Path('extensions/*/')]

        assert radish.cli.match(lines, paths) == {
            'extensions/cool-extension/',
            'extensions/warm-extension/'
        }


class TestConfigParser(object):
    def test_reads_a_list_of_paths(self):
        conf_file = StringIO('\n'.join([
            '---',
            'paths:',
            '  - extensions/',
            '  - frontend/js'
        ]))

        assert radish.cli.read_config(conf_file) == {
            'paths': [Path('extensions/'), Path('frontend/js')],
            'commands': set()
        }

    def test_expands_a_globbed_path(self):
        from path import Path

        with Path('tests/support/dummy/'):
            assert radish.cli.read_config('Radishfile')['paths'] == [
                Path('extensions/roles_and_permissions/'),
                Path('extensions/rules/'),
                Path('js/mobile/')
            ]

    def test_reads_a_list_of_commands_for_paths(self):
        conf_file = StringIO('\n'.join([
            '---',
            'paths:',
            '  - extensions/',
            '  - frontend/js',
            'commands:',
            '  test:',
            '    default: python setup.py test',
            '    frontend/js: npm test'
        ]))

        config = radish.cli.read_config(conf_file)

        assert config['commands'] == {
            Command('test', {
                'default': 'python setup.py test',
                'frontend/js': 'npm test'
            })
        }
