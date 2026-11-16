\set ON_ERROR_STOP on

BEGIN;

CREATE ROLE r09_app NOLOGIN NOSUPERUSER NOBYPASSRLS;

CREATE SCHEMA r09lab;

CREATE TABLE r09lab.measurements (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant_id text NOT NULL,
    reading integer NOT NULL
);

INSERT INTO r09lab.measurements (tenant_id, reading)
VALUES
    ('tenant_a', 101),
    ('tenant_a', 102),
    ('tenant_b', 201),
    ('tenant_b', 202);

ALTER TABLE r09lab.measurements ENABLE ROW LEVEL SECURITY;
ALTER TABLE r09lab.measurements FORCE ROW LEVEL SECURITY;

CREATE POLICY r09_tenant_isolation
ON r09lab.measurements
FOR ALL
TO r09_app
USING (
    tenant_id = NULLIF(
        current_setting('app.tenant_id', true), ''
    )
)
WITH CHECK (
    tenant_id = NULLIF(
        current_setting('app.tenant_id', true), ''
    )
);

GRANT USAGE ON SCHEMA r09lab TO r09_app;

GRANT SELECT, INSERT, UPDATE, DELETE
ON r09lab.measurements TO r09_app;

GRANT USAGE, SELECT
ON ALL SEQUENCES IN SCHEMA r09lab
TO r09_app;

COMMIT;
