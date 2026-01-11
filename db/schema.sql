CREATE TABLE IF NOT EXISTS employers (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(255),
    vacancies_count INT
);

CREATE TABLE IF NOT EXISTS vacancies (
    id BIGINT PRIMARY KEY,
    employer_id BIGINT NOT NULL REFERENCES employers(id),
    title VARCHAR(255) NOT NULL,
    salary_from NUMERIC,
    salary_to NUMERIC,
    currency VARCHAR(50),
    url VARCHAR(255),
    experience VARCHAR(100),
    schedule VARCHAR(100)
);