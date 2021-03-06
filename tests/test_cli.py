from __future__ import unicode_literals

import os
from io import StringIO

from docopt import DocoptExit

from radish.executor import ExecutionResult, ExecutionResults

try:
    from unittest import mock
except ImportError:
    import mock

import pytest
from path import path

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

    class TestFindCommand(object):
        def test_returns_the_named_command_if_it_exists(self, cli):
            assert cli.find_command('test')

        def test_returns_none_when_nothing_found(self, cli):
            assert cli.find_command('wololooo') is None

    @mock.patch('concurrent.futures.as_completed')
    @mock.patch('concurrent.futures.ThreadPoolExecutor')
    class TestRunParallelization(object):
        def test_default_parallelization_of_1(self, futures_executor, as_completed, cli):
            pool_executor = futures_executor.return_value

            cli.run('test', ['extensions/rules/'])

            futures_executor.assert_called_once_with(max_workers=1)
            pool_executor.__enter__.return_value.submit.assert_called_once_with(mock.ANY, mock.ANY, mock.ANY)
            as_completed.assert_called_once_with(mock.ANY)

        def test_accepts_a_jobs_argument_that_sets_the_max_workers(self, futures_executor, _, cli):
            cli.run('test', ['extensions/rules/'], jobs=3)

            futures_executor.assert_called_once_with(max_workers=3)

        def test_handles_exceptions_when_resolving_futures(self, futures_executor, as_completed,
                                                           cli):
            pool_executor = futures_executor.return_value
            future = pool_executor.__enter__.return_value.submit.return_value
            future.result.side_effect = Exception('Boom!')
            as_completed.return_value.__iter__.return_value = [future]

            cli.run('test', ['extensions/rules/'])

            error_output = cli.outputter.error.streams[0].getvalue()
            assert (
                'Command for path "extensions/rules/" generated an exception: Exception('
            ) in error_output
            assert "'Boom!',)" in error_output
            assert 'extensions/rules/' in cli.results.paths
            assert not cli.results.success

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
        assert sorted(results.paths) == sorted(paths)

    def test_passed_in_can_be_a_command_instance(self, cli):
        command = cli.find_command('test')
        paths = list(cli.changed_projects())

        cli.run(command, paths)

        assert cli.results.success

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


class TestGetConfigFile(object):
    def test_raises_exception_if_the_file_isnt_found(self):
        with pytest.raises(OSError) as exc:
            radish.cli.get_config_file('wololooo')

        assert exc.value.args[0] == 'No file "wololooo" found'

    def test_any_of_the_passed_in_file_exists_the_absolute_path_gets_returned(self):
        with path('tests/support/dummy/'):
            found_file = radish.cli.get_config_file('wololoo', 'Radishfile')

            assert found_file == os.path.join(os.getcwd(), 'Radishfile')


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


def assert_command(cli_args, exit_code):
    with pytest.raises(radish.cli.RadishExit) as exc:
        with path('tests/support/dummy/'):
            radish.cli.main(cli_args)

    assert exc.value.code == exit_code


class TestMain(object):
    def test_no_passed_arguments_gives_the_version(self, ):
        with pytest.raises(DocoptExit) as exc:
            radish.cli.main([])

        assert 'Usage:' in exc.value.usage

    @mock.patch('radish.cli.CLI', autospec=True)
    class TestCommand(object):
        def test_invalid_command(self, cli_mock, cli):
            cli_mock.return_value = cli

            assert_command(['command', 'wololooo'], (
                'No command "wololooo" registered.\n\n'
                'Available commands:\n'
                '\ttest'
            ))

        def test_finds_command_successfully_print_status_on_outputter(self, cli_mock, outputter):
            results = ExecutionResults()
            results.add(ExecutionResult(0, 1.12, 'extensions/m000/'))

            cli = cli_mock.return_value
            cli.outputter = outputter
            cli.changed_projects.return_value = ['extensions/m000/']
            cli.run.return_value = results

            assert_command(['command', 'test'], 0)
            assert cli.outputter.info.streams[0].getvalue() == (
                'Changed paths:\n'
                '\textensions/m000/\n\n'
                'extensions/m000/: Success (1.12)\n\n'
                'Finished in less than 0.000 seconds\n'
            )

        def test_unsuccessful_command_run_exits_10(self, cli_mock):
            results = ExecutionResults()
            results.add(ExecutionResult(1, 0.2, '/'))

            cli = cli_mock.return_value
            cli.outputter = mock.create_autospec(Outputter())
            cli.run.return_value = results

            assert_command(['command', 'test'], 10)

    @mock.patch('radish.cli.CLI', autospec=True)
    class TestParallelization(object):
        def _setup(self, cli_mock, outputter):
            results = ExecutionResults()
            results.add(ExecutionResult(0, 1.12, 'extensions/m000/'))

            cli = cli_mock.return_value
            cli.outputter = outputter
            cli.changed_projects.return_value = ['extensions/first/', 'extensions/m000/']
            cli.run.return_value = results

            return cli

        def test_runs_only_a_limited_number_of_projects_when_jobs_and_job_set(self, cli_mock,
                                                                              outputter):
            cli = self._setup(cli_mock, outputter)

            assert_command(['command', 'test', '--jobs', '2', '--job', '1'], 0)

            assert 'in parallel as job 2/2' in cli.outputter.info.streams[0].getvalue()
            assert cli.run.call_count == 1
            args, kwargs = cli.run.call_args
            assert kwargs['paths'] == ['extensions/m000/']
            assert kwargs['jobs'] == 1

        def test_runs_all_in_parallel_when_no_job_index_specified(self, cli_mock, outputter):
            cli = self._setup(cli_mock, outputter)

            assert_command(['command', 'test', '--jobs', '2'], 0)

            assert cli.run.call_count == 1
            args, kwargs = cli.run.call_args
            assert kwargs['jobs'] == 2
            assert 'in parallel with 2 processes' in cli.outputter.info.streams[0].getvalue()

        def test_prints_actual_time_spent_running(self, cli_mock, outputter):
            cli = self._setup(cli_mock, outputter)

            assert_command(['command', 'test', '--jobs', '2'], 0)

            run_time = (
                'Cumulative run time: 1.12 seconds\n'
                'Finished in less than 0.000 seconds\n'
            )
            assert run_time in cli.outputter.info.streams[0].getvalue()
            assert cli.outputter.info.streams[0].getvalue().endswith(run_time)
