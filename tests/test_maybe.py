from __future__ import unicode_literals

from io import StringIO

from path import path

import maybe
from maybe import Path


class TestMatch(object):
    def test_returns_nothing_for_no_matches(self):
        lines = ['test/m000.py']
        paths = [Path('extensions/cool-extension')]

        assert maybe.match(lines, paths) == set()

    def test_returns_unique_matched_paths(self):
        lines = [
            'extensions/cool-extension/src/a.py',
            'extensions/cool-extension/tests/test_a.py'
        ]
        paths = [Path('extensions/cool-extension/')]

        assert maybe.match(lines, paths) == {'extensions/cool-extension/'}

    def test_returns_unique_matched_globbed_directories(self):
        lines = [
            'extensions/cool-extension/src/a.py',
            'extensions/warm-extension/src/b.py'
        ]
        paths = [Path('extensions/*/')]

        assert maybe.match(lines, paths) == {
            'extensions/cool-extension/',
            'extensions/warm-extension/'
        }


class TestConfigParser(object):
    def test_reads_a_list_of_paths(self):
        conf_file = StringIO('\n'.join([
            '---',
            'paths:',
            '  - extensions/',
            '  - frontend/js'
        ]))

        assert maybe.read_config(conf_file) == {
            'paths': [Path('extensions/'), Path('frontend/js')],
            'commands': set()
        }

    def test_expands_a_globbed_path(self):
        with path('tests/support/dummy/'):
            assert maybe.read_config('Maybefile')['paths'] == [
                Path('extensions/roles_and_permissions/'),
                Path('extensions/rules/'),
                Path('js/mobile/')
            ]

    def test_reads_a_list_of_commands_for_paths(self):
        conf_file = StringIO('\n'.join([
            '---',
            'paths:',
            '  - extensions/',
            '  - frontend/js',
            'commands:',
            '  test:',
            '    default: python setup.py test',
            '    frontend/js: npm test'
        ]))

        config = maybe.read_config(conf_file)

        assert config['commands'] == {
            maybe.Command('test', {
                'default': 'python setup.py test',
                'frontend/js': 'npm test'
            })
        }
