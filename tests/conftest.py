from __future__ import unicode_literals

from io import StringIO

import pytest

from maybe import Command
from maybe import Path
from maybe.cli import CLI
from maybe.executioners import NullExecutioner
from maybe.outputter import Outputter, OutputStream


@pytest.fixture
def command():
    return Command(
        name='test',
        mapping={
            'default': 'python setup.py test',
            'extensions/warm-extension/': 'npm test',
            'ruby/*/': 'bundle exec rspec',
        }
    )

@pytest.fixture()
def outputter():
    return Outputter(StringIO(), StringIO())


@pytest.fixture
def stream():
    return OutputStream()


@pytest.fixture
def config():
    return dict(
        paths=[Path('extensions/rules/'), Path('js/frontend/'), Path('js/mobile/')],
        commands={Command('test', {
            'extensions/rules/': 'py.test',
            'js/*/': 'npm test'
        })}
    )


@pytest.fixture
def executioner(outputter):
    return NullExecutioner(0, outputter=outputter)


@pytest.fixture
def cli(config, outputter, executioner):
    return CLI(
        base_path='tests/support/dummy/',
        config=config,
        executioner=executioner,
        outputter=outputter,
    )
