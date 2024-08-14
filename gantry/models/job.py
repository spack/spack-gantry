from gantry.util.time import webhook_timestamp


class Job:
    def __init__(
        self,
        status: str,
        gl_id: int,
        start: str,
        end: str,
        ref: str,
    ):
        self.status = status
        self.gl_id = gl_id
        # handle jobs that haven't started or finished
        if start:
            self.start = webhook_timestamp(start)
        if end:
            self.end = webhook_timestamp(end)

        self.ref = ref

    @property
    def midpoint(self) -> float:
        """Returns the midpoint of the job in unix time."""
        # prometheus is not guaranteed to have data at the exact start and end times
        # instead of creating an arbitrary buffer, ask for data in the middle of the job
        return (self.start + self.end) / 2
