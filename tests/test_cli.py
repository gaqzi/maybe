from __future__ import unicode_literals


class TestCli(object):
    FIRST_GREEN_COMMIT = '10aac02e05'
    FIRST_GREEN_COMMIT_PY = '39e0889d06'

    def test_changed_projects_returns_all_configured_paths_with_no_commits_given(self, cli):
        assert cli.changed_projects() == {'extensions/rules/', 'js/frontend/', 'js/mobile/'}

    def test_changed_projects_returns_only_the_ones_with_changed_files(self, cli):
        assert cli.changed_projects(
            from_commit=self.FIRST_GREEN_COMMIT,
            to_commit=self.FIRST_GREEN_COMMIT_PY
        ) == {'extensions/rules/'}

    def test_will_run_the_passed_in_command_for_all_configured_folders(self, cli):
        paths = list(cli.changed_projects())

        results = cli.run('test', paths)

        assert cli.successful
        assert len(results.paths) == 3
        assert results.paths == paths

    def test_returns_empty_result_when_theres_no_matched_paths(self, cli):

        results = cli.run('test', ['error/'])

        assert cli.successful
        assert results.paths == []
        assert results.run_time == 0.0

    def test_executing_command_outputs_info_about_what_is_running_and_where(self, cli):
        cli.run('test', ['extensions/rules/'])

        out = cli.outputter.info.streams[0].getvalue()
        assert out == 'Running test for extensions/rules/:\n\n'
