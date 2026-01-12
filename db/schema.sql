import mysql.connector

def create_mysql_db():
    conn = mysql.connector.connect(
        host='localhost',
        user='your_user',
        password='your_password',
        database='jobs_db'
    )
    cursor = conn.cursor()

    # Ваши таблицы
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employers (
            id BIGINT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            url VARCHAR(255),
            vacancies_count INT
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vacancies (
            id BIGINT PRIMARY KEY,
            employer_id BIGINT NOT NULL,
            title VARCHAR(255) NOT NULL,
            salary_from NUMERIC,
            salary_to NUMERIC,
            currency VARCHAR(50),
            url VARCHAR(255),
            experience VARCHAR(100),
            schedule VARCHAR(100),
            FOREIGN KEY (employer_id) REFERENCES employers(id)
        );
    ''')

    conn.commit()
    cursor.close()
    conn.close()
    print("MySQL БД создана!")

if __name__ == '__main__':
    create_mysql_db()
