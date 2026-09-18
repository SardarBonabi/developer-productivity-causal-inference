-- Representative staging schema only. Research under review; full code/data proprietary.
-- No production schema, connection details, cohort manifests or raw records included.
CREATE TABLE collection_checkpoint (
    project text NOT NULL,
    snapshot text NOT NULL,
    stage text NOT NULL,
    partition_key text NOT NULL,
    next_cursor text,
    complete boolean NOT NULL DEFAULT false,
    revision bigint NOT NULL DEFAULT 0 CHECK (revision >= 0),
    updated_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (project, snapshot, stage, partition_key),
    CHECK (NOT complete OR next_cursor IS NULL)
);

CREATE TABLE collection_record (
    project text NOT NULL,
    snapshot text NOT NULL,
    stage text NOT NULL,
    record_key text NOT NULL,
    payload jsonb NOT NULL CHECK (jsonb_typeof(payload) = 'object'),
    PRIMARY KEY (project, snapshot, stage, record_key)
);
-- Private analytical tables materialize typed developer-week, repository-language,
-- developer-project-week and pull-request grains from these validated stage records.
