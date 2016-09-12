import pytest

from maybe import Command, CommandResults, CommandResult, Path
from maybe.executioners import NullExecutioner


@pytest.fixture
def command():
    return Command(
        name='test',
        mapping={
            'default': 'python setup.py test',
            'extensions/warm-extension/': 'npm test',
            'ruby/*/': 'bundle exec rspec',
        }
    )


class TestCommand(object):
    def test_commands_are_equal_if_the_values_are_equal(self):
        assert Command(name='test',
                       mapping=dict(a='npm test')) == Command(name='test',
                                                              mapping=dict(a='npm test'))

    def test_commands_should_be_comparable_in_sets(self):
        assert {Command(name='test',
                        mapping=dict(a='npm test'))} == {Command(name='test',
                                                                 mapping=dict(a='npm test'))}

    def test_items_returns_a_list_of_path_cmd_strings(self, command):
        assert command.items() == [
            ('default', 'python setup.py test'),
            ('ruby/*/', 'bundle exec rspec'),
            ('extensions/warm-extension/', 'npm test'),
        ]

    def test_items_takes_a_list_of_paths_to_only_return_commands_for(self, command):
        assert command.items(filter=['extensions/warm-extension/']) == [
            ('extensions/warm-extension/', 'npm test'),
        ]

    def test_items_returned_takes_default_command_into_consideration(self, command):
        assert command.items(filter=['something/else/']) == [
            ('something/else/', 'python setup.py test'),
        ]

    def test_items_will_match_against_globs(self, command):
        assert command.items(filter=['ruby/mobile/']) == [
            ('ruby/mobile/', 'bundle exec rspec')
        ]


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

    def test_paths_doesnt_retain_none_paths(self):
        result = CommandResults()
        result.add(CommandResult.none())

        assert result.paths == []

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

    def test_none_factory_method(self):
        assert CommandResult.none() == CommandResult(0, 0, None)
