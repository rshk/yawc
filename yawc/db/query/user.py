from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql.dml import insert

import bcrypt
from yawc import db

from ..schema.user import UsersTable


def create_user(name, email, password):
    query = (
        insert(UsersTable)
        .values(
            name=name,
            email=email,
            password=_encrypt_password(password)))
    result = db.execute(query)
    user_id, = result.inserted_primary_key
    return user_id


def list_users():
    query = (
        select([UsersTable])
        .order_by(UsersTable.c.id.asc()))
    result = db.execute(query)
    yield from result.fetchall()


def get_user(id):
    query = (
        select([UsersTable])
        .where(UsersTable.c.id == id))
    result = db.execute(query)
    return result.fetchone()


def get_user_by_email(email):
    query = (
        select([UsersTable])
        .where(UsersTable.c.email == email))
    result = db.execute(query)
    return result.fetchone()


def get_user_by_name(name):
    query = (
        select([UsersTable])
        .where(UsersTable.c.name == name))
    result = db.execute(query)
    return result.fetchone()


def verify_credentials(email, password):
    user = get_user_by_email(email)
    if not user:
        return None
    if _verify_password(password, user.password):
        return user
    return None


def set_user_password(userid, password):
    hashed = _encrypt_password(password)
    query = (
        update(UsersTable)
        .values(password=hashed)
        .where(UsersTable.c.id == userid))
    db.execute(query)


def delete_user(userid):
    query = (
        delete(UsersTable)
        .where(UsersTable.c.id == userid))
    db.execute(query)


def _encrypt_password(password):
    if isinstance(password, str):
        password = password.encode()
    return bcrypt.hashpw(password, bcrypt.gensalt()).decode()


def _verify_password(password, hashed):
    if isinstance(password, str):
        password = password.encode()
    if isinstance(hashed, str):
        hashed = hashed.encode()
    return bcrypt.checkpw(password, hashed)
