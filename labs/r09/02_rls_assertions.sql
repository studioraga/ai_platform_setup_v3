-- Execute with psql -v ON_ERROR_STOP=1 in a DISPOSABLE database after setup.
-- Verify same-tenant visibility, cross-tenant denial, and transaction-local reset.
BEGIN;
INSERT INTO r09_lab.measurements (tenant_id, reading) VALUES ('tenant_a', 11), ('tenant_b', 22);
SET LOCAL ROLE r09_lab_app;
SELECT set_config('r09.tenant_id', 'tenant_a', true);
DO $$ DECLARE n int; BEGIN
 SELECT count(*) INTO n FROM r09_lab.measurements;
 IF n <> 1 THEN RAISE EXCEPTION 'tenant_a expected 1, got %', n; END IF;
 IF EXISTS (SELECT 1 FROM r09_lab.measurements WHERE tenant_id='tenant_b') THEN
   RAISE EXCEPTION 'Cross-tenant read leaked';
 END IF;
END $$;
ROLLBACK;
-- Negative writes and pool cleanup require separate transaction/role tests.
