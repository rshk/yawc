from sqlalchemy import select
from sqlalchemy.dialects.postgresql.dml import insert

from yawc import db

from ..schema.chat import MessagesTable


def list_messages(channel):
    query = (
        select([MessagesTable])
        .where(MessagesTable.c.channel == channel)
        .order_by(MessagesTable.c.id.asc()))
    result = db.execute(query)
    yield from result.fetchall()


def post_message(channel, text, *, user_id):
    query = (
        insert(MessagesTable)
        .values(
            channel=channel,
            user_id=user_id,
            text=text))
    result = db.execute(query)
    msg_id, = result.inserted_primary_key
    return get_message_by_id(msg_id)


def get_message_by_id(id):
    query = (
        select([MessagesTable])
        .where(MessagesTable.c.id == id))
    result = db.execute(query)
    return result.fetchone()
