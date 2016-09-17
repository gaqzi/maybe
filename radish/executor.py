from __future__ import unicode_literals

import os
import subprocess
from io import StringIO

import six

from radish.outputter import Outputter
from radish.utils import timer, TimeTaken


class BaseExecutor(object):
    _base_path = None

    def execute(self, path, command):
        raise NotImplementedError('execute is not implemented')

    def _null_response(self):
        return ExecutionResult.none()

    @property
    def base_path(self):
        return self._base_path

    @base_path.setter
    def base_path(self, path):
        self._base_path = os.path.abspath(path)


class NullExecutor(BaseExecutor):
    def __init__(self, exit_code, run_time=0, output='', base_path='.', outputter=None):
        self.exit_code = exit_code
        self.run_time = run_time
        self.output = output
        self.base_path = base_path

        self.outputter = outputter or Outputter(StringIO(), StringIO())

        self.command = None

    def execute(self, path, command):
        self.command = command
        if command is None:
            return self._null_response()

        self.outputter.info.write(six.text_type(self.output))
        return ExecutionResult(self.exit_code, self.run_time, path)


class Executor(BaseExecutor):
    def __init__(self, outputter=None, base_path='.'):
        if outputter is None:
            outputter = Outputter()

        self.outputter = outputter
        self.base_path = base_path

    def execute(self, path, command):
        if command is None:
            return self._null_response()

        process, run_time = timer(lambda: self._run(command, path))

        return ExecutionResult(
            exit_code=process.returncode,
            run_time=run_time,
            path=path,
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
            self.outputter.info.write(six.text_type(stdout.decode('utf-8')))
            self.outputter.error.write(six.text_type(stderr.decode('utf-8')))

        return process

    def _make_absolute_path(self, path):
        if not os.path.isabs(path):
            path = os.path.abspath(os.path.join(self.base_path, path))

        return path


class ExecutionResult(object):
    def __init__(self, exit_code, run_time, path):
        self.exit_code = exit_code
        self.run_time = run_time
        self.path = path

    @property
    def success(self):
        return True if self.exit_code == 0 else False

    def __bool__(self):
        return self.success

    def __nonzero__(self):
        return self.__bool__()

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @classmethod
    def none(cls):
        """Returns a null object version of :class:`CommandResult`

        Returns:
            ExecutionResult: with all values set to 0 or None
        """
        return cls(0, 0, None)


class ExecutionResults(object):
    def __init__(self):
        self._results = []

    def add(self, result):
        """

        Args:
            result (ExecutionResult): The results of running a command for a given path
        """
        self._results.append(result)

    @property
    def success(self):
        if self._results:
            return all(self._results)
        else:
            return False

    @property
    def run_time(self):
        return sum(map(lambda x: x.run_time, self._results), TimeTaken(0))

    @property
    def paths(self):
        return [x.path for x in self._results if x.path is not None]

    def __bool__(self):
        return self.success

    def __nonzero__(self):
        return self.__bool__()

    def __getitem__(self, item):
        return self._results[item]
