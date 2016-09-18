from time import sleep

import pytest

from radish.utils import timer, TimeTaken


class TestTimer(object):
    def test_returns_the_return_value_of_the_passed_in_callable(self):
        return_value, _ = timer(lambda: 'Hello')

        assert return_value == 'Hello'

    def test_records_the_time_taken_for_passed_in_callable(self):
        _, run_time = timer(lambda: sleep(0.01))

        assert run_time.elapsed_time.total_seconds() > 0


class TestTimeTaken(object):
    class TestStr(object):
        def test_taken_more_than_an_hour(self):
            assert str(TimeTaken(3662.19)) == '1 hour, 1 minute, and 2.19 seconds'

        def test_taken_exactly_on_the_hour(self):
            assert str(TimeTaken(3600)) == '1 hour'
            assert str(TimeTaken(7200)) == '2 hours'

        def test_taken_less_than_an_hour(self):
            assert str(TimeTaken(150.40)) == '2 minutes and 30.4 seconds'

        def test_taken_exactly_on_the_minute(self):
            assert str(TimeTaken(60.0)) == '1 minute'
            assert str(TimeTaken(120.0)) == '2 minutes'

        def test_taken_less_than_a_minute(self):
            assert str(TimeTaken(30.5)) == '30.5 seconds'
            assert str(TimeTaken(1)) == '1.0 second'
            assert str(TimeTaken(0.1)) == '0.1 seconds'

        def test__str__and__unicode__returns_the_same(self):
            time = TimeTaken(30.5)

            assert time.__str__() == time.__unicode__()

    class TestRepr(object):
        def test_output_info_about_timedelta(self):
            assert TimeTaken(0).__repr__() == 'TimeTaken(elapsed_time=datetime.timedelta(0))'

    class TestAddAndRemoveTimeTaken(object):
        def test_add_two_time_taken(self):
            assert (TimeTaken(1) + TimeTaken(1)).elapsed_time.total_seconds() == 2.0

        def test_adding_other_objects_gets_passed_down_to_timedelta(self):
            with pytest.raises(TypeError, message='asdf'):
                TimeTaken(1) + 'm000'

        def test_adding_int_and_float_gets_converted_to_timedelta_before_passed_on(self):
            assert (TimeTaken(1) + 1).elapsed_time.total_seconds() == 2.0
            assert (TimeTaken(1) + 1.0).elapsed_time.total_seconds() == 2.0

        def test_subtract_time_taken(self):
            assert (TimeTaken(2) - TimeTaken(1)).elapsed_time.total_seconds() == 1.0

        def test_subtracting_other_objects_gets_passed_down_to_timedelta(self):
            with pytest.raises(TypeError, message='asdf'):
                TimeTaken(1) - 'm000'

        def test_subtracting_int_and_float_gets_converted_to_timedelta_before_passed_on(self):
            assert (TimeTaken(2) - 1).elapsed_time.total_seconds() == 1.0
            assert (TimeTaken(2) - 1.0).elapsed_time.total_seconds() == 1.0

    class TestEquality(object):
        def test_equal_if_the_same_elapsed_time(self):
            assert TimeTaken(1) == TimeTaken(1)

        def test_equalling_other_objects_gets_passed_down_to_timedelta(self):
            assert TimeTaken(1) != 'm000'

        def test_equal_successfully_against_integers_and_floats(self):
            assert TimeTaken(2) == 2
            assert TimeTaken(2.3) != 2
            assert TimeTaken(2.3) == 2.3
