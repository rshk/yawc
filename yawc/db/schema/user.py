from sqlalchemy import BigInteger, Column, DateTime, Table, Text

from yawc.db.connection import metadata
from yawc.utils.dates import utcnow

UsersTable = Table(
    'users', metadata,

    Column('id', BigInteger, primary_key=True),

    Column('email', Text, index=True, unique=True, nullable=False),
    Column('name', Text, index=True, unique=True, nullable=False),
    Column('password', Text, nullable=False),

    Column('date_created',
           DateTime(timezone=True), default=utcnow, nullable=False),
    Column('date_updated',
           DateTime(timezone=True), default=utcnow, onupdate=utcnow,
           nullable=False),
)
