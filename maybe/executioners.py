from __future__ import unicode_literals

import os
import subprocess
from io import StringIO

import six

from maybe.command import CommandResult
from maybe.outputter import Outputter
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
    def __init__(self, exit_code, run_time=0, output='', base_path='.', outputter=None):
        self.exit_code = exit_code
        self.run_time = run_time
        self.output = output
        self.base_path = base_path

        self.outputter = outputter or Outputter(StringIO(), StringIO())

        self.command = None

    def run(self, path, command):
        self.command = command
        if command is None:
            return self._null_response()

        self.outputter.info.write(six.text_type(self.output))
        return CommandResult(self.exit_code, self.run_time, path)


class Executioner(BaseExecutioner):
    def __init__(self, outputter=None, base_path='.'):
        if outputter is None:
            outputter = Outputter()

        self.outputter = outputter
        self.base_path = base_path

    def run(self, path, command):
        if command is None:
            return self._null_response()

        process, run_time = timer(lambda: self._run(command, path))

        return CommandResult(
            exit_code=process.returncode,
            run_time=run_time.total_seconds(),
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
            self.outputter.info.write(six.text_type(stdout))
            self.outputter.error.write(six.text_type(stderr))

        return process

    def _make_absolute_path(self, path):
        if not os.path.isabs(path):
            path = os.path.abspath(os.path.join(self.base_path, path))

        return path
