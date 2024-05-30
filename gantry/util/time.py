import datetime


def webhook_timestamp(dt: str) -> float:
    """Converts a gitlab webhook datetime to a unix timestamp."""
    # gitlab sends dates in 2021-02-23 02:41:37 UTC format
    # documentation says they use iso 8601, but they don't consistently apply it
    # https://docs.gitlab.com/ee/user/project/integrations/webhook_events.html#job-events
    GITLAB_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S %Z"
    # strptime doesn't tag with timezone by default
    return (
        datetime.datetime.strptime(dt, GITLAB_DATETIME_FORMAT)
        .replace(tzinfo=datetime.timezone.utc)
        .timestamp()
    )
