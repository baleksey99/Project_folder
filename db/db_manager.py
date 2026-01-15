from typing import Dict, List
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()



class DBManager:
    def __init__(self):
        # Сначала подключаемся к БД 'postgres' (стандартная БД для администрирования)
        self.conn = psycopg2.connect(
            dbname="postgres",  # Базовая БД для выполнения CREATE DATABASE
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )

    def create_database(self):
        """Создать БД, если её ещё нет."""
        db_name = os.getenv("DB_NAME")
        if not db_name:
            raise ValueError("DB_NAME не задан в .env")

        with self.conn.cursor() as cur:
            # Проверяем, существует ли БД
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            if cur.fetchone():
                print(f"БД '{db_name}' уже существует.")
                return

            # Создаём БД
            cur.execute(f"CREATE DATABASE {db_name}")
            print(f"БД '{db_name}' создана.")

        self.conn.commit()

    def connect_to_database(self):
        """Переподключиться к целевой БД (после её создания)."""
        self.conn.close()
        self.conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )

    def create_tables(self):
        """Создать таблицы в БД."""
        dir_path = os.path.dirname(os.path.abspath(__file__))
        schema_path = os.path.join(dir_path, "schema.sql")

        with open(schema_path, "r", encoding="utf-8") as f:
            sql = f.read()

        with self.conn.cursor() as cur:
            cur.execute(sql)
        self.conn.commit()
        print("Таблицы созданы.")

    def insert_employer(self, employer: Dict):
        """Добавить компанию в БД."""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO employers (id, name, url, vacancies_count)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE
                SET name = EXCLUDED.name,
                    url = EXCLUDED.url,
                    vacancies_count = EXCLUDED.vacancies_count
            """, (
                employer["id"],
                employer["name"],
                employer["alternate_url"],
                employer.get("open_vacancies", 0)
            ))
        self.conn.commit()

    def insert_vacancy(self, vacancy: Dict):
        """Добавить вакансию в БД. Предварительно убедиться, что работодатель существует."""
        employer_id = vacancy["employer"]["id"]
        employer_name = vacancy["employer"]["name"]
        employer_url = vacancy["employer"]["alternate_url"]

        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM employers WHERE id = %s",
                (employer_id,)
            )
            if not cur.fetchone():
                cur.execute(
                    """
                    INSERT INTO employers (id, name, url, vacancies_count)
                    VALUES (%s, %s, %s, 0)
                    """,
                    (employer_id, employer_name, employer_url)
                )

        salary = vacancy.get("salary", {}) or {}
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO vacancies (
                    id, employer_id, title, salary_from, salary_to, currency, url, experience, schedule
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                vacancy["id"],
                employer_id,
                vacancy["name"],
                salary.get("from"),
                salary.get("to"),
                salary.get("currency"),
                vacancy["alternate_url"],
                (vacancy.get("experience") or {}).get("name"),
                (vacancy.get("schedule") or {}).get("name")
            ))
        self.conn.commit()

    def get_companies_and_vacancies_count(self) -> List:
        """Список компаний и количество вакансий."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT name, vacancies_count FROM employers ORDER BY vacancies_count DESC")
            return cur.fetchall()


    def get_all_vacancies(self) -> List[Dict]:
        """Все вакансии с данными."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    e.name AS company_name,
                    v.title,
                    v.salary_from,
                    v.salary_to,
                    v.currency,
                    v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.id
            """)
            return cur.fetchall()

    def get_avg_salary(self) -> float:
        """Средняя зарплата по вакансиям."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT AVG((salary_from + salary_to) / 2) FROM vacancies
                WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
            """)
            result = cur.fetchone()[0]
            return round(result, 2) if result else 0.0

    def get_vacancies_with_higher_salary(self) -> List[Dict]:
        """Вакансии с зарплатой выше средней."""
        avg_salary = self.get_avg_salary()
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    e.name AS company_name,
                    v.title,
                    COALESCE(v.salary_from, 0) + COALESCE(v.salary_to, 0) / 2 AS avg_salary,
                    v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.id
                WHERE (COALESCE(v.salary_from, 0) + COALESCE(v.salary_to, 0)) / 2 > %s
            """, (avg_salary,))
            return cur.fetchall()

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict]:
        """Вакансии по ключевому слову."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    e.name AS company_name,
                    v.title,
                    v.salary_from,
                    v.salary_to,
                    v.currency,
                    v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.id
                WHERE LOWER(v.title) LIKE LOWER(%s)
            """, (f"%{keyword}%",))
            return cur.fetchall()
