from __future__ import unicode_literals

import os
import subprocess
import sys
from io import StringIO

import six

from maybe.command import CommandResult
from maybe.utils import timer


class BaseExecutioner(object):
    _base_path = None

    def run(self, path, command):
        raise NotImplementedError('run is not implemented')

    def _null_response(self):
        return CommandResult.none()

    @property
    def base_path(self):
        return self._base_path

    @base_path.setter
    def base_path(self, path):
        self._base_path = os.path.abspath(path)


class NullExecutioner(BaseExecutioner):
    def __init__(self, exit_code, run_time=0, output='', stdout=None, stderr=None, base_path='.'):
        self.exit_code = exit_code
        self.run_time = run_time
        self.output = output
        self.base_path = base_path

        self.stdout = stdout or StringIO()
        self.stderr = stderr or StringIO()

        self.command = None

    def run(self, path, command):
        self.command = command
        if command is None:
            return self._null_response()

        self.stdout.write(six.text_type(self.output))
        return CommandResult(self.exit_code, self.run_time, path)


class Executioner(BaseExecutioner):
    def __init__(self, stdout=sys.stdout, stderr=sys.stderr, base_path='.'):
        self.stdout = stdout
        self.stderr = stderr
        self.base_path = base_path

    def run(self, path, command):
        if command is None:
            return self._null_response()

        self._add_command_output_logging()
        process, run_time = timer(lambda: self._run(command, path))

        self._result_stdout.seek(0)
        self._result_stderr.seek(0)

        return CommandResult(
            exit_code=process.returncode,
            run_time=run_time.total_seconds(),
            path=path,
            output=self._result_stdout.read(),
            stderr=self._result_stderr.read()
        )

    def _run(self, command, path):
        """

        Args:
            command (str): the command to execute
            path (Path): the path where the command should be executed

        Returns:
            subprocess.Popen: A finished popen process
        """
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=self._make_absolute_path(str(path)),
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )

        while process.returncode is None:
            stdout, stderr = process.communicate()
            self._stdout(six.text_type(stdout))
            self._stderr(six.text_type(stderr))

        return process

    def _make_absolute_path(self, path):
        if not os.path.isabs(path):
            path = os.path.abspath(os.path.join(self.base_path, path))

        return path

    def _stdout(self, string):
        self.stdout.write(string)
        if callable(getattr(self._result_stdout, 'write', None)):
            self._result_stdout.write(string)

    def _stderr(self, string):
        self.stderr.write(string)
        if callable(getattr(self._result_stderr, 'write', None)):
            self._result_stderr.write(string)

    def _add_command_output_logging(self):
        self._result_stdout = StringIO()
        self._result_stderr = StringIO()

        # def _remove_command_output_logging(self):
        #     delattr(self, '_result_stdout')
        #     delattr(self, '_result_stderr')
