DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'querypilot_app') THEN
        CREATE ROLE querypilot_app LOGIN PASSWORD 'querypilot_app';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'querypilot_reader') THEN
        CREATE ROLE querypilot_reader LOGIN PASSWORD 'querypilot_reader';
    END IF;
END
$$;

ALTER ROLE querypilot_app NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;
ALTER ROLE querypilot_reader NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION;

REVOKE ALL ON DATABASE querypilot FROM PUBLIC;
GRANT CONNECT ON DATABASE querypilot TO querypilot_app, querypilot_reader;

ALTER DATABASE querypilot OWNER TO querypilot_app;
ALTER SCHEMA public OWNER TO querypilot_app;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT USAGE, CREATE ON SCHEMA public TO querypilot_app;
GRANT USAGE ON SCHEMA public TO querypilot_reader;

ALTER ROLE querypilot_app IN DATABASE querypilot SET search_path = public;
ALTER ROLE querypilot_reader IN DATABASE querypilot SET search_path = public;
ALTER ROLE querypilot_reader IN DATABASE querypilot SET default_transaction_read_only = on;
ALTER ROLE querypilot_reader IN DATABASE querypilot SET statement_timeout = '5s';
