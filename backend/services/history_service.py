from database.simple import Database
from entities.list_history import InsertListHistory, ListHistoryExtended
from enums.list_history_action import ListHistoryAction
from repositories import list_history_repo
from services.permissions import check_access_for_list


async def append_log(
    *,
    db: Database,
    list_id: int,
    action: ListHistoryAction,
    item_id: int,
    details: str | None,
    actor_id: int | None,
) -> None:
    await list_history_repo.insert_list_history_log(
        db,
        log=InsertListHistory(
            list_id=list_id,
            action=action,
            item_id=item_id,
            details=details,
            actor_id=actor_id,
        ),
    )


async def get_list_history(
    *,
    db: Database,
    list_id: int,
    user_id: int | None,
    share_token: str | None,
    actions: list[ListHistoryAction] | None,
) -> list[ListHistoryExtended]:
    list_ = await check_access_for_list(
        db=db,
        list_id=list_id,
        user_id=user_id,
        share_token=share_token,
    )
    return await list_history_repo.get_list_history_extended_logs(
        db,
        list_id=list_.id,
        actions=actions,
    )
