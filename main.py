import sys
import logging
from typing import List, Optional

from api.hh_api import HeadHunterAPI
from models.vacancy import Vacancy
from storage.json_saver import ConcreteJSONSaver
from db.db_manager import DBManager  # Импорт DBManager

# Настройка логирования (исправлено: levelname → levelname)
logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)s: %(message)s"
)


def _create_vacancy_from_api_item(item: dict) -> Optional[Vacancy]:
    """
    Создаёт объект Vacancy из сырых данных API.
    Возвращает None при ошибках валидации.
    """
    try:
        # Проверка обязательных полей
        title = item.get("name", "").strip()
        if not title:
            return None

        if 'id' not in item or not item['id']:
            return None

        # Формирование URL
        url = f"https://hh.ru/vacancy/{item['id']}"

        # Обработка зарплаты
        salary = item.get("salary")
        salary_str = None
        if salary:
            salary_from = str(salary.get('from', ''))
            salary_to = str(salary.get('to', ''))
            currency = str(salary.get('currency', ''))
            salary_str = f"{salary_from}–{salary_to} {currency}".strip()
            # Ограничение длины строки зарплаты
            if len(salary_str) > 100:
                salary_str = salary_str[:97] + "..."

        # Описание
        snippet = item.get("snippet") or {}
        description = str(snippet.get("requirement", "")).strip() or ""

        return Vacancy(title=title, url=url, salary=salary_str, description=description)

    except (KeyError, ValueError, TypeError, AttributeError) as e:
        logging.warning(f"Ошибка создания Vacancy: {e} | Данные: {dict(list(item.items())[:3])}")
        return None



def user_interaction():
    """
    Функция взаимодействия с пользователем.
    Реализует консольный интерфейс для поиска, фильтрации и сохранения вакансий.
    """
    print("Добро пожаловать в систему поиска вакансий на hh.ru!\n")

    # Инициализация компонентов
    hh_api = HeadHunterAPI()
    json_saver = ConcreteJSONSaver("vacancies.json")
    db_manager = DBManager()  # Инициализация DBManager
    db_manager.create_tables()  # Создание таблиц (если их нет)

    try:
        # Шаг 1. Ввод параметров поиска
        search_query = input("Введите поисковый запрос (например, 'Python разработчик'): ").strip()
        if not search_query:
            print("Ошибка: запрос не может быть пустым.")
            return

        # Обработка количества вакансий в топе
        try:
            top_n_input = input("Сколько вакансий показать в топе по зарплате? (по умолчанию 5): ").strip()
            top_n = int(top_n_input) if top_n_input else 5
            if top_n < 1:
                top_n = 1
            elif top_n > 50:
                top_n = 50
        except ValueError:
            top_n = 5

        filter_words = input(
            "Введите ключевые слова для фильтрации описания (через пробел, например, 'опыт git'): "
        ).strip().split()

        # Шаг 2. Получение вакансий с hh.ru
        print(f"\nИщем вакансии по запросу '{search_query}'...")
        raw_vacancies = hh_api.get_vacancies(query=search_query, per_page=20)

        if not raw_vacancies:
            print("По вашему запросу вакансии не найдены.")
            return

        # Шаг 3. Преобразование в объекты Vacancy и сохранение в БД
        vacancies: List[Vacancy] = []
        for item in raw_vacancies:
            vacancy = _create_vacancy_from_api_item(item)
            if vacancy:
                vacancies.append(vacancy)
                # Сохранение сырых данных в PostgreSQL
                db_manager.insert_vacancy(item)
            else:
                logging.warning(f"Пропущена некорректная вакансия: {item.get('name', 'без названия')}")


        if not vacancies:
            print("Не удалось преобразовать ни одну вакансию.")
            return

        print(f"\nНайдено {len(vacancies)} вакансий.\n")

        # Шаг 4. Фильтрация по ключевым словам в описании
        if filter_words:
            filtered = [
                v for v in vacancies
                if any(word.lower() in v.description.lower() for word in filter_words)
            ]
            print(f"После фильтрации по ключевым словам осталось {len(filtered)} вакансий.")
        else:
            filtered = vacancies

        # Шаг 5. Сортировка по зарплате (убывание)
        sorted_vacancies = sorted(filtered, key=lambda v: v.get_salary_value() or 0, reverse=True)

        # Шаг 6. Топ N по зарплате
        top_vacancies = sorted_vacancies[:top_n]

        # Шаг 7. Вывод результатов
        print(f"\nТоп {len(top_vacancies)} вакансий по зарплате:\n")
        for i, vacancy in enumerate(top_vacancies, 1):
            print(f"{i}. {vacancy.title}")
            print(f"Зарплата: {vacancy.salary}")
            print(f"Ссылка: {vacancy.url}")
            if vacancy.description:
                print(f"Описание: {vacancy.description[:150]}...")
            print("-! * 80")

        # Шаг 8. Сохранение в JSON (по запросу пользователя)
        save_choice = input("\nСохранить найденные вакансии в файл vacancies.json? (да/нет): ").strip().lower()
        if save_choice in ("да", "y", "yes"):
            for vacancy in sorted_vacancies:
                json_saver.add_vacancy(vacancy.to_dict())
            print("Вакансии сохранены в файл vacancies.json.")

        # Шаг 9. Демонстрация данных из PostgreSQL
        print()
        print("=" * 50)
        print("ДАННЫЕ ИЗ БД:")

        # 1. Компании и количество вакансий
        companies = db_manager.get_companies_and_vacancies_count()
        print(f"\nКомпании и количество вакансий:")
        for c in companies:
            print(f"- {c['name']}: {c['vacancies_count']} вакансий")

        # 2. Средняя зарплата
        avg_salary = db_manager.get_avg_salary()
        print(f"\nСредняя зарплата по всем вакансиям: {avg_salary}")

        # 3. Вакансии с зарплатой выше средней
        high_salary = db_manager.get_vacancies_with_higher_salary()
        print(f"\nВакансий с зарплатой выше средней: {len(high_salary)}")
        for v in high_salary[:3]:  # Топ-3
            print(f"- {v['company_name']}: {v['title']} ({v['avg_salary']})")

        # 4. Поиск по ключевому слову
        keyword = "python"
        keyword_vacancies = db_manager.get_vacancies_with_keyword(keyword)
        print(f"\nВакансий с ключевым словом '{keyword}': {len(keyword_vacancies)}")
        for v in keyword_vacancies[:3]:
            print(f"- {v['company_name']}: {v['title']}")

    except ValueError as e:
        print(f"Ошибка ввода: {e}")
    except ConnectionError as e:
        print(f"Ошибка подключения к API: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")



def main():
    """
    Точка входа в программу.
    Запускает интерактивное взаимодействие с пользователем.
    """
    try:
        user_interaction()
    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем.")
        sys.exit(0)
    except Exception as e:
        print(f'Критическая ошибка: {e}')
        sys.exit(1)



if __name__ == "__main__":
    main()
