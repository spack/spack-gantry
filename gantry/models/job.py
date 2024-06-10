import re

from gantry.util.time import webhook_timestamp


class Job:
    def __init__(
        self,
        status: str,
        name: str,
        gl_id: int,
        start: str,
        end: str,
        ref: str,
    ):
        self.status = status
        self.name = name
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

    @property
    def valid_build_name(self) -> bool:
        """validates the job name."""

        # example: plumed@2.9.0 /i4u7p6u %gcc@11.4.0
        # arch=linux-ubuntu20.04-neoverse_v1 E4S ARM Neoverse V1
        job_name_pattern = re.compile(
            r"([^/ ]+)@([^/ ]+) /([^%]+) %([^ ]+) ([^ ]+) (.+)"
        )
        job_name_match = job_name_pattern.match(self.name)
        # groups: 1: name, 2: version, 3: hash, 4: compiler, 5: arch, 6: stack
        return bool(job_name_match)
