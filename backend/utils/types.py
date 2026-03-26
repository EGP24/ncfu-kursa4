from typing import Any, cast


def cast_optional[T: Any](value: T | None) -> T:
    return cast(T, value)
