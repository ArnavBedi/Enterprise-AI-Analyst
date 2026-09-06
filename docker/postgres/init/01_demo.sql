CREATE TABLE IF NOT EXISTS employees (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text NOT NULL,
    department text NOT NULL,
    age integer NOT NULL,
    salary numeric(12, 2) NOT NULL
);

INSERT INTO employees (name, department, age, salary)
SELECT * FROM (VALUES
    ('Avery', 'Engineering', 31, 85000.00),
    ('Jordan', 'Engineering', 36, 90000.00),
    ('Morgan', 'Finance', 42, 90000.00),
    ('Riley', 'Marketing', 29, 79000.00),
    ('Casey', 'Marketing', 34, 84000.00)
) AS seed(name, department, age, salary)
WHERE NOT EXISTS (SELECT 1 FROM employees);

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'analyst_reader') THEN
        CREATE ROLE analyst_reader LOGIN PASSWORD 'analyst_reader_password';
    END IF;
END
$$;

GRANT CONNECT ON DATABASE analytics TO analyst_reader;
GRANT USAGE ON SCHEMA public TO analyst_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analyst_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO analyst_reader;
ALTER ROLE analyst_reader SET default_transaction_read_only = on;
