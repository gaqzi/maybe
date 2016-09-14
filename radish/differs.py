from __future__ import unicode_literals

import logging
import os
import sys
from io import StringIO

import six

if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess

logger = logging.getLogger(__name__)


class Git(object):
    _command = 'git'
    _base_path = None

    def __init__(self, base_path='.'):
        self.base_path = base_path

    def changed_files_between(self, from_commit, to_commit=None):
        return self._run(['diff', '--name-only', from_commit, to_commit])

    @property
    def base_path(self):
        return self._base_path

    @base_path.setter
    def base_path(self, value):
        self._base_path = os.path.abspath(value)

    def _run(self, arguments):
        command = [self._command]
        command.extend(arguments)
        command = filter(lambda x: x, command)  # Remove empty arguments

        output = StringIO()
        stderr = StringIO()

        process = subprocess.Popen(
            ' '.join(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(self.base_path),
            universal_newlines=True,
            shell=True
        )

        while process.returncode is None:
            out, err = process.communicate()
            output.write(six.u(out))
            stderr.write(six.u(err))

        output.seek(0)
        stderr.seek(0)

        if process.returncode == 0:
            return filter(lambda x: x, output.read().strip().split('\n'))
        else:
            logger.warn('Command exited unsuccessfully', extra=dict(
                stdout=output.read(),
                stderr=stderr.read(),
                exit_status=process.returncode,
                command=command
            ))
            output.seek(0)
            stderr.seek(0)

            raise subprocess.CalledProcessError(
                process.returncode,
                command,
                "STDOUT:\n{0}\n-----\nSTDERR:\n{1}\n".format(output.read(),
                                                             stderr.read())
            )
