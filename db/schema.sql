-- Создание таблицы работодателей
CREATE TABLE IF NOT EXISTS employers (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(500),
    vacancies_count INT DEFAULT 0
);

-- Создание таблицы вакансий
CREATE TABLE IF NOT EXISTS vacancies (
    id BIGINT PRIMARY KEY,
    employer_id BIGINT NOT NULL,
    title VARCHAR(255) NOT NULL,
    salary_from NUMERIC(10, 2),
    salary_to NUMERIC(10, 2),
    currency VARCHAR(10),
    url VARCHAR(500),
    experience VARCHAR(100),
    schedule VARCHAR(100),
    CONSTRAINT fk_employer 
        FOREIGN KEY (employer_id)
        REFERENCES employers(id)
        ON DELETE CASCADE
);