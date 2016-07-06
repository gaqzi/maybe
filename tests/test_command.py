from maybe import Command, CommandResults, CommandResult, Path
from maybe.executioner import NullExecutioner


class TestCommand(object):
    def test_run_command(self):
        command = Command(
            name='test',
            mapping={
                'extensions/cool-extension/': 'python setup.py test',
                'extensions/warm-extension/': 'npm test',
            }
        )
        command.executioner = NullExecutioner(exit_code=0, run_time=0.01, output='.... OK')

        result = command.run(paths=[Path('extensions/cool-extension/')])

        assert result.success
        assert result.run_time == 0.01
        assert result.paths == [Path('extensions/cool-extension/')]
        assert command.executioner.command == 'python setup.py test'
        assert command.executioner.stdout.getvalue() == '.... OK'

    def test_run_command_with_default_path(self):
        command = Command(name='test', mapping=dict(default='python setup.py test'))
        command.executioner = NullExecutioner(exit_code=0, run_time=0.01, output='.... OK')

        command.run(paths=[Path('extensions/cool-extension/')])

        assert command.executioner.command == 'python setup.py test'

    def test_commands_are_equal_if_the_values_are_equal(self):
        assert Command(name='test', mapping=dict(a='npm test')) == Command(name='test', mapping=dict(a='npm test'))

    def test_commands_should_be_comparable_in_sets(self):
        assert {Command(name='test', mapping=dict(a='npm test'))} == {Command(name='test', mapping=dict(a='npm test'))}


class TestCommandResults(object):
    def test_no_results_is_negative(self):
        result = CommandResults()

        assert not result.success

    def test_converts_to_boolean_using_success(self):
        result = CommandResults()

        assert bool(result) == result.success

    def test_add_successful_result_sets_success_to_true(self):
        result = CommandResults()
        result.add(CommandResult(0, 0.1, '/m000'))

        assert result.success

    def test_add_negative_result_sets_success_to_false(self):
        result = CommandResults()
        result.add(CommandResult(1, 0.1, '/m000'))

        assert not result.success

    def test_run_time_with_no_values_is_0(self):
        assert CommandResults().run_time == 0

    def test_aggregates_run_times(self):
        result = CommandResults()
        result.add(CommandResult(0, 0.1, '/m000'))
        result.add(CommandResult(0, 1.0, '/meep'))

        assert result.run_time == 1.1

    def test_no_results_no_paths(self):
        assert CommandResults().paths == []

    def test_results_returns_list_of_paths_results_are_for(self):
        result = CommandResults()
        result.add(CommandResult(0, 0.1, '/m000'))
        result.add(CommandResult(0, 1.0, '/meep'))

        assert result.paths == ['/m000', '/meep']


class TestCommandResult(object):
    def test_exit_code_0_is_success(self):
        assert CommandResult(0, 0.1, '/m000').success

    def test_exit_code_is_nonzero_is_not_successful(self):
        assert not CommandResult(1, 0.1, '/m000').success

    def test_converts_to_boolean_using_success(self):
        result = CommandResult(1, 0.1, '/m000')

        assert bool(result) == result.success

    def test_stores_run_time_in_seconds(self):
        assert CommandResult(0, 0.1, '/m000').run_time == 0.1

    def test_stores_path(self):
        assert CommandResult(0, 0.1, '/m000').path == '/m000'

    def test_command_results_are_equal_if_they_contain_the_same_attrs(self):
        assert CommandResult(0, 0.1, '/m000') == CommandResult(0, 0.1, '/m000')
