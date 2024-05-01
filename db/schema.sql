PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS nodes (
    id INTEGER PRIMARY KEY,
    uuid TEXT NOT NULL UNIQUE,
    hostname TEXT NOT NULL,
    cores REAL NOT NULL,
    mem REAL NOT NULL,
    arch TEXT NOT NULL,
    os TEXT NOT NULL,
    instance_type TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY,
    pod TEXT NOT NULL UNIQUE,
    node INTEGER NOT NULL,
    start INTEGER NOT NULL,
    end INTEGER NOT NULL,
    gitlab_id INTEGER NOT NULL UNIQUE,
    job_status TEXT NOT NULL,
    ref TEXT NOT NULL,
    pkg_name TEXT NOT NULL,
    pkg_version TEXT NOT NULL,
    pkg_variants TEXT NOT NULL,
    compiler_name TEXT NOT NULL,
    compiler_version TEXT NOT NULL,
    arch TEXT NOT NULL,
    stack TEXT NOT NULL,
    build_jobs INTEGER NOT NULL,
    cpu_request REAL NOT NULL,
    cpu_limit REAL, -- this can be null because it's currently not set
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
    FOREIGN KEY (node)
        REFERENCES nodes (id)
            ON UPDATE CASCADE
            ON DELETE CASCADE
);
