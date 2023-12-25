CREATE TABLE vms (
    id INTEGER PRIMARY KEY,
    start INTEGER NOT NULL,
    -- VM end is the max of the build end times
    hostname TEXT NOT NULL,
    cores REAL NOT NULL,
    mem REAL NOT NULL,
    arch TEXT NOT NULL,
    os TEXT NOT NULL,
    instance_type TEXT NOT NULL
);


CREATE TABLE builds (
    -- TODO do we want an entry here for if the job has been retried?
    id INTEGER PRIMARY KEY,
    pod TEXT NOT NULL UNIQUE,
    vm INTEGER NOT NULL,
    start INTEGER NOT NULL,
    end INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    job_status TEXT NOT NULL,
    ref TEXT NOT NULL,
    pkg_name TEXT NOT NULL,
    pkg_version TEXT NOT NULL,
    pkg_variants TEXT NOT NULL, -- can be stored as JSONB in the future?
    compiler_name TEXT NOT NULL,
    compiler_version TEXT NOT NULL,
    arch TEXT NOT NULL,
    stack TEXT NOT NULL,
    build_jobs INTEGER NOT NULL,
    cpu_request REAL NOT NULL,
    cpu_limit REAL, -- this can be null
    cpu_mean REAL NOT NULL,
    cpu_median REAL NOT NULL,
    cpu_max REAL NOT NULL,
    cpu_min REAL NOT NULL,
    cpu_stddev REAL NOT NULL,
    mem_request REAL NOT NULL,
    mem_limit REAL NOT NULL,
    mem_mean REAL NOT NULL,
    mem_median REAL NOT NULL,
    mem_max REAL NOT NULL,
    mem_min REAL NOT NULL,
    mem_stddev REAL NOT NULL,
    FOREIGN KEY (vm)
        REFERENCES vms (id)
            ON UPDATE CASCADE
            ON DELETE CASCADE
);

CREATE TABLE ghost_jobs (
    id INTEGER PRIMARY KEY,
    job_id INTEGER NOT NULL
);
