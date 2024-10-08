import datetime

from gantry.util.const import GITLAB_DATETIME_FORMAT


def webhook_timestamp(dt: str) -> float:
    """Converts a gitlab webhook datetime to a unix timestamp."""
    return (
        datetime.datetime.strptime(dt, GITLAB_DATETIME_FORMAT)
        # strptime doesn't tag with timezone by default
        .replace(tzinfo=datetime.timezone.utc).timestamp()
    )
