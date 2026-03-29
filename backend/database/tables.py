import sqlalchemy as sa


metadata = sa.MetaData()

users_table = sa.Table(
    'users',
    metadata,
    sa.Column('id', sa.BIGINT, primary_key=True),
    sa.Column('username', sa.VARCHAR, nullable=False, unique=True),
    sa.Column('password_hash', sa.VARCHAR, nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
)

lists_table = sa.Table(
    'lists',
    metadata,
    sa.Column('id', sa.BIGINT, primary_key=True),
    sa.Column('title', sa.VARCHAR, nullable=False),
    sa.Column('owner_id', sa.BIGINT, nullable=False),
    sa.Column('share_token', sa.VARCHAR, nullable=True, unique=True),
    sa.Column('is_deleted', sa.BOOLEAN, nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False),
)

items_table = sa.Table(
    'items',
    metadata,
    sa.Column('id', sa.BIGINT, primary_key=True),
    sa.Column('list_id', sa.BIGINT, nullable=False),
    sa.Column('name', sa.VARCHAR, nullable=False),
    sa.Column('quantity', sa.NUMERIC(10, 2), nullable=False),
    sa.Column('unit', sa.VARCHAR, nullable=True),
    sa.Column('checked', sa.BOOLEAN, nullable=False),
    sa.Column('position', sa.BIGINT, nullable=False),
    sa.Column('manual_position', sa.BIGINT, nullable=False),
    sa.Column('is_deleted', sa.BOOLEAN, nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False),
)

list_history_table = sa.Table(
    'list_history',
    metadata,
    sa.Column('id', sa.BIGINT, primary_key=True),
    sa.Column('list_id', sa.BIGINT, nullable=False),
    sa.Column('action', sa.VARCHAR, nullable=False),
    sa.Column('item_id', sa.BIGINT, nullable=False),
    sa.Column('details', sa.TEXT, nullable=True),
    sa.Column('actor_id', sa.BIGINT, nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
)
