from datetime import datetime
from pytz import utc


def utcnow():
    return datetime.utcnow().replace(tzinfo=utc)
