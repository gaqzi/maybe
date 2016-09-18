# coding=utf-8
from __future__ import unicode_literals

import os

from radish.executor import ExecutionResult, NullExecutor, Executor, ExecutionResults
from radish.outputter import Outputter
from radish.path import Path
from radish.utils import TimeTaken

try:
    from unittest.mock import Mock, ANY
except ImportError:
    from mock import Mock, ANY


class BaseTestExecutor(object):
    def test_command_is_none_returns_none_result(self):
        executor = self._executor()

        result = executor.execute(Path('/tmp'), None)

        assert result == ExecutionResult.none(), 'Result was not none'

    def _executor(self):
        raise NotImplementedError('Has not implemented _executor()')


class TestNullExecutor(BaseTestExecutor):
    def _executor(self):
        return NullExecutor(0)

    def test_takes_a_base_path_argument(self):
        assert NullExecutor(0, base_path='.').base_path == os.path.abspath('.')

    def test_run_returns_command_result_with_passed_in_exit_code(self):
        executor = self._executor()

        assert executor.execute(Path('/m000'), 'true') == ExecutionResult(0, 0, Path('/m000'))

    def test_sets_run_time_on_result(self):
        executor = NullExecutor(0, run_time=1)

        assert executor.execute(Path('/m000'), 'true') == ExecutionResult(0, 1, Path('/m000'))

    def test_run_writes_output_to_output_stream(self):
        outputter = Mock()
        executor = NullExecutor(0, output='Hello!', outputter=outputter)
        executor.execute(Path('/m000'), 'true')

        outputter.info.write.assert_called_once_with('Hello!')


class TestExecutor(BaseTestExecutor):
    def _executor(self):
        return Executor(outputter=Mock())

    def test_takes_a_base_path_argument(self):
        assert Executor(base_path='.').base_path == os.path.abspath('.')

    def test_run_returns_command_result_success_when_successful(self):
        executor = Executor()

        result = executor.execute(Path('/tmp'), 'true')

        assert result.success, 'Expected command to exit successfully'
        assert result.run_time != 0.0

    def test_run_returns_command_result_failure_when_command_fails(self):
        executor = Executor()

        result = executor.execute(Path('/tmp'), 'false')

        assert not result.success, 'Expected command to not exit successfully'
        assert result.run_time != 0.0

    def test_it_accepts_an_outputter(self):
        Executor(outputter=Outputter())

    def test_run_outputs_through_outputter(self):
        outputter = Mock()
        executor = Executor(outputter=outputter)

        executor.execute(Path('/tmp'), 'echo hello')

        outputter.info.write.assert_called_once_with('hello\n')

    def test_run_stderr_outputs_through_outputter(self):
        outputter = Mock()
        executor = Executor(outputter=outputter)

        executor.execute(Path('/tmp'), 'echoz hello')

        outputter.error.write.assert_called_once_with(ANY)
        assert 'echoz' in outputter.error.write.call_args[0][0]

    def test_decode_output_to_utf8_before_writing(self):
        outputter = Mock()
        executor = Executor(outputter=outputter)

        executor.execute(Path('/tmp'), 'echo Björn')

        outputter.info.write.assert_called_once_with('Björn\n')


class TestExecutionResults(object):
    def test_no_results_is_negative(self):
        result = ExecutionResults()

        assert not result.success

    def test_converts_to_boolean_using_success(self):
        result = ExecutionResults()

        assert bool(result) == result.success

    def test_boolean_for_both_py2_and_py3(self):
        result = ExecutionResults()

        assert result.__bool__() == result.__nonzero__()

    def test_add_successful_result_sets_success_to_true(self):
        result = ExecutionResults()
        result.add(ExecutionResult(0, 0.1, '/m000'))

        assert result.success

    def test_add_negative_result_sets_success_to_false(self):
        result = ExecutionResults()
        result.add(ExecutionResult(1, 0.1, '/m000'))

        assert not result.success

    def test_run_time_with_no_values_is_0(self):
        assert ExecutionResults().run_time == 0

    def test_aggregates_run_times(self):
        result = ExecutionResults()
        result.add(ExecutionResult(0, 0.1, '/m000'))
        result.add(ExecutionResult(0, 1.0, '/meep'))

        assert result.run_time == 1.1

    def test_run_times_returns_a_time_taken_instance(self):
        result = ExecutionResults()
        result.add(ExecutionResult(0, 0.1, '/m000'))

        assert isinstance(result.run_time, TimeTaken)

    def test_no_results_no_paths(self):
        assert ExecutionResults().paths == []

    def test_paths_doesnt_retain_none_paths(self):
        result = ExecutionResults()
        result.add(ExecutionResult.none())

        assert result.paths == []

    def test_results_returns_list_of_paths_results_are_for(self):
        result = ExecutionResults()
        result.add(ExecutionResult(0, 0.1, '/m000'))
        result.add(ExecutionResult(0, 1.0, '/meep'))

        assert result.paths == ['/m000', '/meep']

    def test_when_iterated_returns_the_results(self):
        result = ExecutionResults()
        result.add(ExecutionResult.none())

        results = list(map(lambda x: x, result))

        assert results == result._results


class TestExecutionResult(object):
    def test_exit_code_0_is_success(self):
        assert ExecutionResult(0, 0.1, '/m000').success

    def test_exit_code_is_nonzero_is_not_successful(self):
        assert not ExecutionResult(1, 0.1, '/m000').success

    def test_converts_to_boolean_using_success(self):
        result = ExecutionResult(1, 0.1, '/m000')

        assert bool(result) == result.success

    def test_boolean_for_both_py2_and_py3(self):
        result = ExecutionResult(1, 0.1, '/m000')

        assert result.__bool__() == result.__nonzero__()

    def test_stores_run_time_in_seconds(self):
        assert ExecutionResult(0, 0.1, '/m000').run_time == 0.1

    def test_stores_path(self):
        assert ExecutionResult(0, 0.1, '/m000').path == '/m000'

    def test_results_are_equal_if_they_contain_the_same_attrs(self):
        assert ExecutionResult(0, 0.1, '/m000') == ExecutionResult(0, 0.1, '/m000')

    def test_none_factory_method(self):
        assert ExecutionResult.none() == ExecutionResult(0, 0, None)
