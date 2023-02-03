from typing import TypeVar

T = TypeVar("T")


def dig(obj, *keys, error=False):
    keys = list(keys)
    if isinstance(keys[0], list):
        return dig(obj, *keys[0], error=error)

    if (
        isinstance(obj, dict)
        and keys[0] in obj
        or isinstance(obj, list)
        and keys[0] < len(obj)
    ):
        if len(keys) == 1:
            return obj[keys[0]]
        return dig(obj[keys[0]], *keys[1:], error=error)

    if hasattr(obj, keys[0]):
        if len(keys) == 1:
            return getattr(obj, keys[0])
        return dig(getattr(obj, keys[0]), *keys[1:], error=error)

    if error:
        raise KeyError(keys[0])

    return None


def none_to_empty_list(obj: T | None) -> T | list:
    if obj is None:
        return []
    else:
        return obj
