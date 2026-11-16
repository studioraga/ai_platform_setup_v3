\set ON_ERROR_STOP on

SET ROLE r09_app;

BEGIN;

SET LOCAL app.tenant_id = 'tenant_a';

-- This role can change its custom session variable.
-- This demonstrates that the value must be protected
-- by the application/trusted identity boundary.

SET LOCAL app.tenant_id = 'tenant_b';

DO $$
DECLARE
    visible_count integer;
BEGIN
    SELECT count(*)
    INTO visible_count
    FROM r09lab.measurements
    WHERE tenant_id = 'tenant_b';

    IF visible_count <> 2 THEN
        RAISE EXCEPTION
            'Unexpected result in context-spoofing experiment';
    END IF;
END
$$;

ROLLBACK;

RESET ROLE;
