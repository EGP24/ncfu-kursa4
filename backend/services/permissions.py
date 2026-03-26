
from database.simple import Database
from entities.list import List
from exceptions import ListNotFound
from repositories import list_repo


async def check_access_for_list(
    *,
    db: Database,
    list_id: int,
    user_id: int | None,
    share_token: str | None,
    side_effect: Exception | None = None,
) -> List:
    side_effect = side_effect or ListNotFound
    list_ = await list_repo.get_list_by_id(db, list_id=list_id)
    if not list_:
        raise side_effect

    if (user_id and list_.owner_id == user_id) or (share_token and list_.share_token == share_token):
        return list_

    raise side_effect
