from StringIO import StringIO

from maybe import CommandResult, Executioner
from maybe import Path
from maybe.executioner import NullExecutioner


class TestNullExecutioner(object):
    def test_run_returns_command_result_with_passed_in_exit_code(self):
        executioner = NullExecutioner(0)

        assert executioner.run(Path('/m000'), 'true') == CommandResult(0, 0, Path('/m000'))

    def test_sets_run_time_on_result(self):
        executioner = NullExecutioner(0, run_time=1)

        assert executioner.run(Path('/m000'), 'true') == CommandResult(0, 1, Path('/m000'))

    def test_run_writes_output_to_output_stream(self):
        executioner = NullExecutioner(0, output='Hello!')
        executioner.run(Path('/m000'), 'true')

        assert executioner.stdout.getvalue() == 'Hello!'


class TestExecutioner(object):
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

    def test_run_outputs_to_stdout(self):
        executioner = Executioner(stdout=StringIO())

        result = executioner.run(Path('/tmp'), 'echo hello')

        assert result.success, 'Expected command to exit successfully'
        assert executioner.stdout.getvalue() == 'hello\n'
