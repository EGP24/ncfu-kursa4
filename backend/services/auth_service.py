from auth import check_password, create_token, hash_password
from database.simple import Database
from entities.auth_result import AuthResult
from entities.user import InsertUser
from exceptions import InvalidCredentials, UserNameTaken
from repositories import user_repo


async def register(*, db: Database, username: str, password: str) -> AuthResult:
    existing = await user_repo.get_user_by_username(db, username=username)
    if existing:
        raise UserNameTaken

    pw_hash = hash_password(password)
    user = await user_repo.insert_user(db, user=InsertUser(username=username, password_hash=pw_hash))
    token = create_token(user.id, user.username)
    return AuthResult(user=user, token=token)


async def login(*, db: Database, username: str, password: str) -> AuthResult:
    user = await user_repo.get_user_by_username(db, username=username.strip())

    if not user or not check_password(password, user.password_hash):
        raise InvalidCredentials

    token = create_token(user.id, user.username)
    return AuthResult(user=user, token=token)
