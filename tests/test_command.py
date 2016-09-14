from __future__ import unicode_literals

from radish.command import Command


class TestCommand(object):
    def test_commands_are_equal_if_the_values_are_equal(self):
        assert Command(name='test',
                       mapping=dict(a='npm test')) == Command(name='test',
                                                              mapping=dict(a='npm test'))

    def test_commands_should_be_comparable_in_sets(self):
        assert {Command(name='test',
                        mapping=dict(a='npm test'))} == {Command(name='test',
                                                                 mapping=dict(a='npm test'))}

    def test_items_returns_a_list_of_path_cmd_strings(self, command):
        assert command.items() == [
            ('default', 'python setup.py test'),
            ('ruby/*/', 'bundle exec rspec'),
            ('extensions/warm-extension/', 'npm test'),
        ]

    def test_items_takes_a_list_of_paths_to_only_return_commands_for(self, command):
        assert command.items(filter=['extensions/warm-extension/']) == [
            ('extensions/warm-extension/', 'npm test'),
        ]

    def test_items_returned_takes_default_command_into_consideration(self, command):
        assert command.items(filter=['something/else/']) == [
            ('something/else/', 'python setup.py test'),
        ]

    def test_items_will_match_against_globs(self, command):
        assert command.items(filter=['ruby/mobile/']) == [
            ('ruby/mobile/', 'bundle exec rspec')
        ]
