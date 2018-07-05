import logging
import os
from contextlib import contextmanager
from urllib.parse import urlparse

from sqlalchemy import MetaData, create_engine

logger = logging.getLogger(__name__)

metadata = MetaData()


class ConfigurationError(Exception):
    pass


def create_engine_from_environment(env=None):
    # config = ConfigurationLoader(env)
    return create_engine(
        os.environ.get('DATABASE_URL'),
        pool_size=20,
        # pool_size=config.get_int('SQLALCHEMY_POOL_SIZE', 20),
        max_overflow=0,
        # max_overflow=config.get_int('SQLALCHEMY_MAX_OVERFLOW', 0),
        # pool_recycle=env['SQLALCHEMY_POOL_RECYCLE'],
        # pool_timeout=env['SQLALCHEMY_POOL_TIMEOUT'],
        # max_overflow=env['SQLALCHEMY_MAX_OVERFLOW'],
        # echo=config.get_bool('SQLALCHEMY_ECHO', False),
        echo=False,
        # echo_pool=config.get_bool('SQLALCHEMY_ECHO_POOL', False)
        echo_pool=False,
    )


_engine = None


def get_engine():
    global _engine
    if not _engine:
        _engine = create_engine_from_environment()
    return _engine


@contextmanager
def connection():
    conn = get_engine().connect()
    yield conn
    conn.close()


@contextmanager
def transaction(conn, autocommit=True, rollback=False):

    trans = conn.begin()

    try:
        yield trans

        if autocommit:
            trans.commit()

        if rollback:
            trans.rollback()

    except Exception:
        trans.rollback()
        raise


def create_all():
    metadata.create_all(get_engine())


def drop_all():
    metadata.drop_all(get_engine())


def make_test_database_url(orig_url):
    PREFIX = 'test_'
    pp = urlparse(orig_url)
    db_name = pp.path[1:]
    if not db_name.startswith(PREFIX):
        db_name = '{}{}'.format(PREFIX, db_name)
    return pp._replace(path=db_name).geturl()


# High-level shortcuts -----------------------------------------------

def execute(*args, **kwargs):
    """Execute one query inside its own transaction"""
    with connection() as conn:
        return conn.execute(*args, **kwargs)
