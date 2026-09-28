CREATE TABLE IF NOT EXISTS departments (
    name text PRIMARY KEY,
    annual_budget numeric(14, 2) NOT NULL,
    region text NOT NULL
);

INSERT INTO departments (name, annual_budget, region) VALUES
    ('Engineering', 1500000.00, 'North America'),
    ('Finance', 900000.00, 'North America'),
    ('Marketing', 1100000.00, 'Europe')
ON CONFLICT (name) DO NOTHING;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'employees_department_fk'
    ) THEN
        ALTER TABLE employees
            ADD CONSTRAINT employees_department_fk
            FOREIGN KEY (department) REFERENCES departments(name);
    END IF;
END
$$;

CREATE TABLE IF NOT EXISTS projects (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text NOT NULL UNIQUE,
    department text NOT NULL REFERENCES departments(name),
    status text NOT NULL,
    budget numeric(14, 2) NOT NULL
);

INSERT INTO projects (name, department, status, budget) VALUES
    ('Platform Modernization', 'Engineering', 'Active', 420000.00),
    ('Forecast Automation', 'Finance', 'Active', 180000.00),
    ('Brand Refresh', 'Marketing', 'Planning', 240000.00)
ON CONFLICT (name) DO NOTHING;

GRANT SELECT ON departments, projects TO analyst_reader;
