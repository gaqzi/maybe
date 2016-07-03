import subprocess
import sys
from StringIO import StringIO

from maybe.command import CommandResult
from maybe.utils import timer


class NullExecutioner(object):
    def __init__(self, exit_code, run_time=0, output='', stdout=None, stderr=None):
        self.exit_code = exit_code
        self.run_time = run_time
        self.output = output

        self.stdout = stdout or StringIO()
        self.stderr = stderr or StringIO()

        self.command = None

    def run(self, path, command):
        self.command = command
        self.stdout.write(self.output)
        return CommandResult(self.exit_code, self.run_time, path)


class Executioner(object):
    def __init__(self, stdout=sys.stdout, stderr=sys.stderr):
        self.stdout = stdout
        self.stderr = stderr

    def run(self, path, command):
        process, run_time = timer(lambda: self._run(command, path))

        return CommandResult(
            exit_code=process.returncode,
            run_time=run_time.total_seconds(),
            path=path
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
            cwd=str(path),
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )

        while process.returncode is None:
            stdout, stderr = process.communicate()
            self.stdout.write(stdout)
            self.stderr.write(stderr)

        return process
