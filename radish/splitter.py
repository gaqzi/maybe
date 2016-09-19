__all__ = ['split']


def split(splittable, splits=None, index=None):
    """Splits a list into :arg:`jobs` chunks

    Args:
        splittable (Sequence[T]): A list of any T to be split into
            jobs chunks
        splits (Union[int, str]): The number of parallel jobs. Default: 1
        index (Union[int, str]): If this is a specified agent of a
            parallel job, this is the split index to return. 0 indexed.
            Default: None, which means return all splits.

    Returns:
        List[T]: list of T split into jobs chunks or the chunk
            specified by index.
    """
    splits = _default_int(splits, 1)
    index = _default_int(index)

    if splits == 1:
        return splittable

    splits = split_consistently(splittable, splits)

    if index:
        return splits[index]
    else:
        return splits


def split_consistently(splittable, splits):
    _splits = [[] for _ in range(0, splits)]

    for i, item in enumerate(splittable):
        _, j = divmod(i, splits)
        _splits[j].append(item)

    return _splits


def _default_int(value, default=None):
    if not value:
        return default
    else:
        return int(value)
