from __future__ import unicode_literals, print_function

import sys


class Outputter(object):
    def __init__(self, info_stream=sys.stdout, error_stream=sys.stderr):
        self.info = OutputStream()
        self.error = OutputStream()

        if info_stream:
            self.info.add(info_stream)

        if error_stream:
            self.error.add(error_stream)


class OutputStream(object):
    class InvalidStream(BaseException):
        pass

    def __init__(self):
        self.streams = []

    def add(self, stream):
        if not self._can_write(stream):
            raise self.InvalidStream('"{0}" does not have a "write" method'.format(
                stream.__class__.__name__)
            )

        self.streams.append(stream)

    def _can_write(self, stream):
        return callable(getattr(stream, 'write', False))

    def write(self, message):
        for stream in self.streams:
            stream.write(message)
