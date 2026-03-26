from collections.abc import Awaitable, Callable
from functools import wraps

from exceptions import ItemNotFound, ListNotFound
from repositories import item_repo, list_repo


def raise_on_none[**P, T](
    side_effect: Exception,
) -> Callable[[Callable[P, Awaitable[T | None]]], Callable[P, Awaitable[T]]]:
    def decorator(func: Callable[P, Awaitable[T | None]]) -> Callable[P, Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            result = await func(*args, **kwargs)
            if result is None:
                raise side_effect
            return result

        return wrapper

    return decorator


get_item_by_id_or_raise = raise_on_none(ItemNotFound)(item_repo.get_item_by_id)
update_item_or_raise = raise_on_none(ItemNotFound)(item_repo.update_item)
get_list_by_id_or_raise = raise_on_none(ListNotFound)(list_repo.get_list_by_id)
get_list_by_share_token_or_raise = raise_on_none(ListNotFound)(list_repo.get_list_by_share_token)
update_list_title_or_raise = raise_on_none(ListNotFound)(list_repo.update_list_title)
delete_list_or_raise = raise_on_none(ListNotFound)(list_repo.delete_list)
set_list_share_token_or_raise = raise_on_none(ListNotFound)(list_repo.set_share_token)
