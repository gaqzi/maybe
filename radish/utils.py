from __future__ import unicode_literals

from datetime import datetime, timedelta


def timer(kallable):
    """

    Args:
        kallable (Callable[[], T):

    Returns:
        (T, TimeTaken): Any return value from the passed in callable
            and the time it took to run it
    """
    start_time = datetime.now()

    return kallable(), TimeTaken(datetime.now() - start_time)


class TimeTaken(object):
    def __init__(self, elapsed_time):
        """Presentation class for :class:`datetime.timedelta`

        Will provide pretty printed hour, minutes, and seconds of time
        elapsed when printed/converted to a string.

        Args:
            elapsed_time (Union[timedelta, int, float]): How much time
                has elapsed
        """
        if not isinstance(elapsed_time, timedelta):
            elapsed_time = timedelta(seconds=elapsed_time)

        self.elapsed_time = elapsed_time  # type: timedelta

    def __str__(self):
        """Elapsed time like: 1 hour, 23 minutes, and 2.3 seconds

        Returns:
            str: Pretty printed time information
        """
        hours, seconds = divmod(self.elapsed_time.total_seconds(), 3600)
        minutes, seconds = divmod(seconds, 60)

        return self._join_output(list(filter(lambda x: x, [
            self._pluralize(int(hours), 'hour', 'hours'),
            self._pluralize(int(minutes), 'minute', 'minutes'),
            self._pluralize(round(seconds, 3), 'second', 'seconds')
        ])))

    __unicode__ = __str__

    def __repr__(self):
        return 'TimeTaken(elapsed_time={})'.format(self.elapsed_time.__repr__())

    def __add__(self, other):
        """Adds the time from another object and returns a new instance

        Args:
            other (Union[TimeTaken, int, float, timedelta]): The object to add

        Returns:
            TimeTaken: A new instance of TimeTaken with the calculation done

        Raises:
            TypeError: For others that can't be used by timedelta
        """
        if hasattr(other, 'elapsed_time'):
            return TimeTaken(self.elapsed_time + other.elapsed_time)
        else:
            if isinstance(other, (int, float)):
                other = timedelta(seconds=other)

        return TimeTaken(self.elapsed_time + other)

    def __sub__(self, other):
        """Adds the time from another object and returns a new instance

        Args:
            other (Union[TimeTaken, int, float, timedelta]): The object to add

        Returns:
            TimeTaken: A new instance of TimeTaken with the calculation done

        Raises:
            TypeError: For others that can't be used by timedelta
        """
        if hasattr(other, 'elapsed_time'):
            return TimeTaken(self.elapsed_time - other.elapsed_time)
        else:
            if isinstance(other, (int, float)):
                other = timedelta(seconds=other)

            return TimeTaken(self.elapsed_time - other)

    def __eq__(self, other):
        if hasattr(other, 'elapsed_time'):
            return self.elapsed_time == other.elapsed_time
        else:
            if isinstance(other, (int, float)):
                other = timedelta(seconds=other)

            return self.elapsed_time == other

    def _pluralize(self, value, singular, plural):
        if value:
            return '{} {}'.format(
                value,
                plural if value > 1 or (1.0 > value > 0.0) else singular
            )

    def _join_output(self, times):
        if len(times) > 2:
            return '{}, and {}'.format(
                ', '.join(times[0:-1]),
                times[-1]
            )
        elif len(times) == 2:
            return ' and '.join(times)
        else:
            return ''.join(times)
