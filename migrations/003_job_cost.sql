-- temporarily disable foreign key constraints
PRAGMA foreign_keys = OFF;

-- this approach is needed because we want to add new columns
-- with a not null constraint, but also to add default values
-- this isn't directly supported by ALTER TABLE

-- create tmp table for nodes
CREATE TABLE nodes_tmp (
    id INTEGER PRIMARY KEY,
    uuid TEXT NOT NULL UNIQUE,
    hostname TEXT NOT NULL,
    cores REAL NOT NULL,
    mem REAL NOT NULL,
    arch TEXT NOT NULL,
    os TEXT NOT NULL,
    instance_type TEXT NOT NULL,
    -- new columns below
    zone TEXT NOT NULL,
    capacity_type TEXT NOT NULL
);

-- copy data from nodes to nodes_tmp
-- '', and '' are the default values for zone, and capacity_type
-- all columns need to be individually selected because we are adding new blank columns
INSERT INTO nodes_tmp SELECT id, uuid, hostname, cores, mem, arch, os, instance_type, '', '' FROM nodes;
DROP TABLE nodes;
ALTER TABLE nodes_tmp RENAME TO nodes;

---- create tmp table for jobs

CREATE TABLE IF NOT EXISTS jobs_tmp (
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
    cpu_cost REAL NOT NULL,
    mem_cost REAL NOT NULL,
    cpu_penalty REAL NOT NULL,
    mem_penalty REAL NOT NULL,
    cost_per_cpu REAL NOT NULL,
    cost_per_mem REAL NOT NULL,
    FOREIGN KEY (node)
        REFERENCES nodes (id)
            ON UPDATE CASCADE
            ON DELETE CASCADE
);

-- copy data from jobs to jobs_tmp
-- all old columns will have cost values set to 0
INSERT INTO jobs_tmp select id, pod, node, start, end, gitlab_id, job_status, ref, pkg_name, pkg_version, pkg_variants, compiler_name, compiler_version, arch, stack, build_jobs, cpu_request, cpu_limit, cpu_mean, cpu_median, cpu_max, cpu_min, cpu_stddev, mem_request, mem_limit, mem_mean, mem_median, mem_max, mem_min, mem_stddev, 0, 0, 0, 0, 0, 0 FROM jobs;
DROP TABLE jobs;
ALTER TABLE jobs_tmp RENAME TO jobs;

PRAGMA foreign_keys = ON;
