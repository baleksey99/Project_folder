import os
import pytest
import time
from api.hh_api import HeadHunterAPI
from models.vacancy import Vacancy
from storage.json_saver import ConcreteJSONSaver


@pytest.fixture
def json_saver():
    filepath = "test_vacancies.json"

    # Пытаемся удалить файл, если он существует
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            # Даём ОС время обработать удаление
            time.sleep(0.1)
        except (OSError, PermissionError) as e:
            print(f"Не удалось удалить файл {filepath}: {e}")

    return ConcreteJSONSaver(filepath)


@pytest.fixture
def hh_api():
    return HeadHunterAPI()


@pytest.fixture
def json_savers():
    return ConcreteJSONSaver("test_vacancies.json")


@pytest.fixture
def sample_vacancy():
    return Vacancy(
        title="Python Developer",
        url="https://hh.ru/vacancy/123",
        salary="100 000–150 000 руб.",
        description="Опыт от 3 лет, знание Django"
    )


@pytest.fixture
def sample_vacancies():
    return [
        Vacancy("Python Dev", "https://...", "100 000 руб.", "Django"),
        Vacancy("JS Developer", "https://...", "80 000 руб.", "React"),
        Vacancy("QA Engineer", "https://...", None, "Тестирование")
    ]
