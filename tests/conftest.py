from __future__ import unicode_literals

from io import StringIO

import pytest

from radish.command import Command
from radish.path import Path
from radish.cli import CLI
from radish.executor import NullExecutor
from radish.outputter import Outputter, OutputStream


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
def executor(outputter):
    return NullExecutor(0, outputter=outputter)


@pytest.fixture
def cli(config, outputter, executor):
    return CLI(
        base_path='tests/support/dummy/',
        config=config,
        executor=executor,
        outputter=outputter,
    )
