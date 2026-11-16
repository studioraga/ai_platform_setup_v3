-- RESEARCH-ONLY. Run in a disposable PostgreSQL database, never production.
-- Execute as DB admin. Do not put real tenant identifiers in tests.
BEGIN;
DO $$ BEGIN
 IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'r09_lab_app') THEN
   CREATE ROLE r09_lab_app NOLOGIN NOSUPERUSER NOBYPASSRLS;
 END IF;
END $$;
CREATE SCHEMA IF NOT EXISTS r09_lab;
CREATE TABLE IF NOT EXISTS r09_lab.measurements (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  tenant_id text NOT NULL,
  reading integer NOT NULL
);
REVOKE ALL ON SCHEMA r09_lab FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA r09_lab FROM PUBLIC;
GRANT USAGE ON SCHEMA r09_lab TO r09_lab_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON r09_lab.measurements TO r09_lab_app;
GRANT USAGE, SELECT ON SEQUENCE r09_lab.measurements_id_seq TO r09_lab_app;
ALTER TABLE r09_lab.measurements ENABLE ROW LEVEL SECURITY;
ALTER TABLE r09_lab.measurements FORCE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS tenant_isolation ON r09_lab.measurements;
CREATE POLICY tenant_isolation ON r09_lab.measurements
 FOR ALL TO r09_lab_app
 USING (tenant_id = current_setting('r09.tenant_id', true))
 WITH CHECK (tenant_id = current_setting('r09.tenant_id', true));
COMMIT;
