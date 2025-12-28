import sys
from typing import List

from api.hh_api import HeadHunterAPI
from models.vacancy import Vacancy
from storage.json_saver import ConcreteJSONSaver  # Исправлено!


def user_interaction():
    """
    Функция взаимодействия с пользователем.
    Реализует консольный интерфейс для поиска, фильтрации и сохранения вакансий.
    """
    print("Добро пожаловать в систему поиска вакансий на hh.ru!\n")

    # Инициализация компонентов
    hh_api = HeadHunterAPI()
    json_saver = ConcreteJSONSaver("vacancies.json")  # Исправлено!

    try:
        # Шаг 1. Ввод параметров поиска
        search_query = input("Введите поисковый запрос (например, 'Python разработчик'): ").strip()
        if not search_query:
            print("Ошибка: запрос не может быть пустым.")
            return

        top_n = input("Сколько вакансий показать в топе по зарплате? (по умолчанию 5): ").strip()
        top_n = int(top_n) if top_n.isdigit() else 5

        filter_words = input(
            "Введите ключевые слова для фильтрации описания (через пробел, например, 'опыт git'): "
        ).strip().split()

        # Шаг 2. Получение вакансий с hh.ru
        print(f"\nИщем вакансии по запросу '{search_query}'...")
        raw_vacancies = hh_api.get_vacancies(query=search_query, per_page=20)

        if not raw_vacancies:
            print("По вашему запросу вакансии не найдены.")
            return

        # Шаг 3. Преобразование в объекты Vacancy
        vacancies: List[Vacancy] = []
        for item in raw_vacancies:
            try:
                title = item.get("name", "")
                url = f"https://hh.ru/vacancy/{item['id']}"  # Исправлено!
                salary = item.get("salary")
                if salary:
                    salary_str = f"{salary.get('from', '')}–{salary.get('to', '')} {salary.get('currency', '')}"
                else:
                    salary_str = None
                description = item.get("snippet", {}).get("requirement", "") or ""

                vacancy = Vacancy(title=title, url=url, salary=salary_str, description=description)
                vacancies.append(vacancy)
            except (ValueError, KeyError) as e:
                print(f"Пропущена некорректная вакансия: {e}")

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
            print(f"   Зарплата: {vacancy.salary}")
            print(f"   Ссылка: {vacancy.url}")
            if vacancy.description:
                print(f"   Описание: {vacancy.description[:150]}...")  # обрезка для компактности
            print("-! * 80")

            # Шаг 8. Сохранение в JSON
            save_choice = input("\nСохранить найденные вакансии в файл vacancies.json? (да/нет): ").strip().lower()
            if save_choice in ("да", "y", "yes"):
                for vacancy in sorted_vacancies:
                    json_saver.add_vacancy(vacancy.to_dict())
            print("Вакансии сохранены в файл vacancies.json.")

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
        print(f"Критическая ошибка: {e}")
        sys.exit(1)

        if __name__ == "__main__":
            main()
