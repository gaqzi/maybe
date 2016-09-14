from __future__ import unicode_literals

from radish.path import Path


class TestPath(object):
    def test_return_false_when_file_doesnt_match(self):
        path = Path('extensions/cool-extension')

        assert not path.match('src/a.py')

    def test_matches_simple_file(self):
        path = Path('extensions/cool-extension/')

        assert path.match('extensions/cool-extension/src/a.py')

    def test_matches_against_glob_expressions(self):
        path = Path('extensions/*/')

        assert path.match('extensions/cool-extension/src/a.py')

    def test_match_against_path_object(self):
        path = Path('extensions/*/')

        assert path.match(Path('extensions/cool-extension/'))

    def test_doesnt_match_against_glob_when_its_a_file(self):
        path = Path('extensions/*/')

        assert not path.match('extensions/cool-extension')

    def test_the_same_path_is_equal(self):
        assert Path('extension/') == Path('extension/')

    def test_path_is_same_as_path_which_would_match_glob(self):
        assert Path('extension/cool-extension/') == Path('extension/*/')

    def test_path_can_compare_to_a_string(self):
        assert Path('extension/cool-extension/') == 'extension/cool-extension/'

    def test_expanded_path(self):
        path = Path('extension/*/')

        assert path.match('extension/cool-extension/') == 'extension/cool-extension/'

    def test_assert_none_paths_are_equal(self):
        assert Path(None) == Path(None)

    def test__str__is_the_path_passed_in(self):
        assert str(Path('hello/')) == 'hello/'

    def test__repr__has_a_marker_for_none_when_its_none(self):
        assert repr(Path(None)) == '<Path: <None>>'

    def test_responds_to_startswith(self):
        assert Path('/root').startswith('/')
        assert not Path('root').startswith('/')

    def test_path_can_be_concatenated_with_a_string(self):
        assert (Path('/') + 'root') == '/root'
        assert ('/' + Path('root')) == '/root'

    def test_path_can_be_concatenated_with_another_path(self):
        assert (Path('/') + Path('root')) == '/root'
