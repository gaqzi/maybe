from radish import splitter


class TestSplit(object):
    def test_splits_one_into_one_piece(self):
        assert splitter.split(['1', '2', '3']) == ['1', '2', '3']

    def test_splits_into_jobs_pieces_consistently(self):
        assert splitter.split(['1', '2', '3'], splits=2) == [['1', '3'], ['2']]

    def test_returns_the_index_specified_by_job_for_a_split(self):
        assert splitter.split(['1', '2', '3'], splits=2, index=1) == ['2']

    def test_splits_empty_splittables(self):
        assert splitter.split([], splits=2) == [[], []]
        assert splitter.split([], splits=2, index=1) == []

    class TestArgumentConversion(object):
        def test_jobs_is_converted_to_integer(self):
            assert splitter.split(['1', '2', '3'], splits='2') == [['1', '3'], ['2']]

        def test_index_is_converted_to_integer(self):
            assert splitter.split(['1', '2', '3'], splits=2, index='1') == ['2']
