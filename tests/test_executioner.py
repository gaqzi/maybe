# coding=utf-8
from __future__ import unicode_literals

import os

from maybe import CommandResult, Executioner
from maybe import Path
from maybe.executioners import NullExecutioner
from maybe.outputter import Outputter

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


class BaseTestExecutioner(object):
    def test_command_is_none_returns_none_result(self):
        executioner = self._executioner()

        result = executioner.run(Path('/tmp'), None)

        assert result == CommandResult.none(), 'Result was not none'

    def _executioner(self):
        raise NotImplementedError('Has not implemented _executioner()')


class TestNullExecutioner(BaseTestExecutioner):
    def _executioner(self):
        return NullExecutioner(0)

    def test_takes_a_base_path_argument(self):
        assert NullExecutioner(0, base_path='.').base_path == os.path.abspath('.')

    def test_run_returns_command_result_with_passed_in_exit_code(self):
        executioner = self._executioner()

        assert executioner.run(Path('/m000'), 'true') == CommandResult(0, 0, Path('/m000'))

    def test_sets_run_time_on_result(self):
        executioner = NullExecutioner(0, run_time=1)

        assert executioner.run(Path('/m000'), 'true') == CommandResult(0, 1, Path('/m000'))

    def test_run_writes_output_to_output_stream(self):
        outputter = Mock()
        executioner = NullExecutioner(0, output='Hello!', outputter=outputter)
        executioner.run(Path('/m000'), 'true')

        outputter.info.write.assert_called_once_with('Hello!')


class TestExecutioner(BaseTestExecutioner):
    def _executioner(self):
        return Executioner(outputter=Mock())

    def test_takes_a_base_path_argument(self):
        assert Executioner(base_path='.').base_path == os.path.abspath('.')

    def test_run_returns_command_result_success_when_successful(self):
        executioner = Executioner()

        result = executioner.run(Path('/tmp'), 'true')

        assert result.success, 'Expected command to exit successfully'
        assert result.run_time != 0.0

    def test_run_returns_command_result_failure_when_command_fails(self):
        executioner = Executioner()

        result = executioner.run(Path('/tmp'), 'false')

        assert not result.success, 'Expected command to not exit successfully'
        assert result.run_time != 0.0

    def test_it_accepts_an_outputter(self):
        Executioner(outputter=Outputter())

    def test_run_outputs_through_outputter(self):
        outputter = Mock()
        executioner = Executioner(outputter=outputter)

        executioner.run(Path('/tmp'), 'echo hello')

        outputter.info.write.assert_called_once_with('hello\n')

    def test_run_stderr_outputs_through_outputter(self):
        outputter = Mock()
        executioner = Executioner(outputter=outputter)

        executioner.run(Path('/tmp'), 'echoz hello')

        outputter.error.write.assert_called_once_with('/bin/sh: echoz: command not found\n')

    def test_decode_output_to_utf8_before_writing(self):
        outputter = Mock()
        executioner = Executioner(outputter=outputter)

        executioner.run(Path('/tmp'), 'echo Björn')

        outputter.info.write.assert_called_once_with('Björn\n')
