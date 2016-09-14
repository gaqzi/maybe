from __future__ import unicode_literals, print_function

import sys
from io import StringIO

import pytest

from radish.outputter import OutputStream


class TestOutputter(object):
    def test_by_default_can_write_to_stdout(self, outputter):
        outputter.info.write('Hello')

        out = outputter.info.streams[0].getvalue()
        assert out == 'Hello'

    def test_by_default_can_write_to_stderr(self, outputter):
        outputter.error.write('There')

        err = outputter.error.streams[0].getvalue()
        assert err == 'There'

    def test_can_add_extra_output_streams(self, outputter):
        stdout = StringIO()
        stderr = StringIO()
        outputter.info.add(stdout)
        outputter.error.add(stderr)

        outputter.info.write('Hello')
        outputter.error.write('There')

        out = outputter.info.streams[0].getvalue()
        err = outputter.error.streams[0].getvalue()
        assert out == 'Hello'
        assert stdout.getvalue() == 'Hello'
        assert err == 'There'
        assert stderr.getvalue() == 'There'


class TestOutputStream(object):
    def test_add_output(self, stream):
        stream.add(sys.stdout)

        assert stream.streams == [sys.stdout]

    def test_writing_with_no_streams_is_a_noop(self, stream):
        stream.write('Hello')

    def test_raises_invalid_stream_for_streams_that_dont_implement_write(self, stream):
        with pytest.raises(OutputStream.InvalidStream) as exc:
            stream.add(None)

        assert exc.value.message == '"NoneType" does not have a "write" method'

    def test_can_write_to_streams(self, stream, capfd):
        output = StringIO()
        stream.add(sys.stdout)
        stream.add(output)

        stream.write('Hello')

        out, err = capfd.readouterr()
        assert out == 'Hello'
        assert output.getvalue() == 'Hello'
        assert err == ''
