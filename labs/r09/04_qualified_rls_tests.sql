\set ON_ERROR_STOP on

SET ROLE r09_app;

BEGIN;

SET LOCAL app.tenant_id = 'tenant_a';

DO $$
DECLARE
    visible_count integer;
    modified_count integer;
BEGIN
    SELECT count(*)
    INTO visible_count
    FROM r09lab.measurements;

    IF visible_count <> 2 THEN
        RAISE EXCEPTION
            'Tenant A expected 2 rows, got %',
            visible_count;
    END IF;

    SELECT count(*)
    INTO visible_count
    FROM r09lab.measurements
    WHERE tenant_id = 'tenant_b';

    IF visible_count <> 0 THEN
        RAISE EXCEPTION
            'Cross-tenant SELECT was permitted';
    END IF;

    UPDATE r09lab.measurements
    SET reading = 999
    WHERE tenant_id = 'tenant_b';

    GET DIAGNOSTICS modified_count = ROW_COUNT;

    IF modified_count <> 0 THEN
        RAISE EXCEPTION
            'Cross-tenant UPDATE affected % rows',
            modified_count;
    END IF;

    DELETE FROM r09lab.measurements
    WHERE tenant_id = 'tenant_b';

    GET DIAGNOSTICS modified_count = ROW_COUNT;

    IF modified_count <> 0 THEN
        RAISE EXCEPTION
            'Cross-tenant DELETE affected % rows',
            modified_count;
    END IF;
END
$$;

-- Must reject an INSERT for another tenant.
DO $$
BEGIN
    BEGIN
        INSERT INTO r09lab.measurements (tenant_id, reading)
        VALUES ('tenant_b', 999);

        RAISE EXCEPTION
            'Cross-tenant INSERT unexpectedly succeeded';

    EXCEPTION
        WHEN insufficient_privilege THEN
            NULL;
    END;
END
$$;

-- An allowed same-tenant INSERT must work.
INSERT INTO r09lab.measurements (tenant_id, reading)
VALUES ('tenant_a', 103);

DO $$
DECLARE
    visible_count integer;
BEGIN
    SELECT count(*)
    INTO visible_count
    FROM r09lab.measurements;

    IF visible_count <> 3 THEN
        RAISE EXCEPTION
            'Same-tenant INSERT not visible';
    END IF;
END
$$;

ROLLBACK;

-- Prove that a new transaction has no tenant context.
BEGIN;

DO $$
DECLARE
    visible_count integer;
BEGIN
    SELECT count(*)
    INTO visible_count
    FROM r09lab.measurements;

    IF visible_count <> 0 THEN
        RAISE EXCEPTION
            'Missing tenant context did not fail closed';
    END IF;
END
$$;

ROLLBACK;

RESET ROLE;
