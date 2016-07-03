from datetime import datetime


def timer(kallable):
    """

    Args:
        kallable (Callable[[], T):

    Returns:
        (T, datetime.timedelta): Any return value from
            the passed in callable and the time it took to run it
    """
    start_time = datetime.now()

    return kallable(), datetime.now() - start_time
