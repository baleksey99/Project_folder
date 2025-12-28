import pytest

from models.vacancy import Vacancy


def test_vacancy_valid_creation():
    """Проверка создания вакансии с корректными данными."""
    vacancy = Vacancy(
        title="Python Developer",
        url="https://hh.ru/vacancy/123",
        salary="100000–150000 руб.",
        description="Опыт от 3 лет, знание Django"
    )

    assert vacancy.title == "Python Developer"
    assert vacancy.url == "https://hh.ru/vacancy/123"
    assert vacancy.salary == "100000–150000 руб."
    assert vacancy.description == "Опыт от 3 лет, знание Django"


def test_vacancy_invalid_title():
    """Проверка валидации пустого названия."""
    with pytest.raises(ValueError, match="Название вакансии не может быть пустым"):
        Vacancy(title="", url="https://example.com")


def test_vacancy_invalid_url():
    """Проверка валидации некорректного URL."""
    with pytest.raises(ValueError, match="Некорректный формат URL"):
        Vacancy(title="Dev", url="invalid-url")

    with pytest.raises(ValueError, match="URL вакансии не может быть пустым"):
        Vacancy(title="Dev", url="")


def test_vacancy_salary_none():
    """Проверка обработки отсутствующей зарплаты."""
    vacancy = Vacancy(title="Dev", url="https://example.com", salary=None)
    assert vacancy.salary == "Зарплата не указана"


def test_vacancy_get_salary_value_no_salary():
    """Проверка get_salary_value для вакансии без зарплаты."""
    vacancy = Vacancy(title="Dev", url="https://example.com", salary="Зарплата не указана")
    assert vacancy.get_salary_value() is None


def test_vacancy_get_salary_value_with_salary():
    """Проверка извлечения числового значения зарплаты."""
    vacancy = Vacancy(title="Dev", url="https://example.com", salary="100000 руб.")
    assert vacancy.get_salary_value() == 100000

    vacancy2 = Vacancy(title="Dev", url="https://example.com", salary="от 80000 до 120 000 руб.")
    assert vacancy2.get_salary_value() == 80000


def test_vacancy_comparison():
    """Проверка сравнения вакансий по зарплате."""
    v1 = Vacancy("Dev1", "https://...", "100 000 руб.")
    v2 = Vacancy("Dev2", "https://...", "80 000 руб.")
    v3 = Vacancy("Dev3", "https://...", "Зарплата не указана")

    assert v1 > v2  # 100k > 80k
    assert v3 < v1  # "не указана" < 100k
    assert v1 >= v2
    assert v2 <= v1
    assert v1 != v2


def test_vacancy_to_dict():
    """Проверка преобразования в словарь."""
    vacancy = Vacancy(
        title="Python Dev",
        url="https://...",
        salary="100000 руб.",
        description="Django"
    )
    expected = {
        "title": "Python Dev",
        "url": "https://...",
        "salary": "100000 руб.",
        "description": "Django"
    }
    assert vacancy.to_dict() == expected


def test_vacancy_from_dict():
    """Проверка создания из словаря."""
    data = {
        "title": "Python Dev",
        "url": "https://...",
        "salary": "100000 руб.",
        "description": "Django"
    }
    vacancy = Vacancy.from_dict(data)
    assert vacancy.title == "Python Dev"
    assert vacancy.url == "https://..."
    assert vacancy.salary == "100000 руб."
    assert vacancy.description == "Django"


def test_vacancy_str():
    """Проверка строкового представления."""
    vacancy = Vacancy("Python Dev", "https://...", "100000 руб.")
    assert str(vacancy) == "Python Dev — 100000 руб. (https://...)"


def test_vacancy_update_title():
    """Проверка изменения названия через сеттер."""
    vacancy = Vacancy("Dev", "https://...")
    vacancy.title = "Senior Dev"
    assert vacancy.title == "Senior Dev"

    with pytest.raises(ValueError, match="Название вакансии не может быть пустым"):
        vacancy.title = ""


def test_vacancy_update_url():
    """Проверка изменения URL через сеттер."""
    vacancy = Vacancy("Dev", "https://...")
    vacancy.url = "https://new-url.com"
    assert vacancy.url == "https://new-url.com"

    with pytest.raises(ValueError, match="Некорректный формат URL"):
        vacancy.url = "invalid-url"


def test_vacancy_update_salary():
    """Проверка изменения зарплаты через сеттер."""
    vacancy = Vacancy("Dev", "https://...")
    vacancy.salary = "200000 руб."
    assert vacancy.salary == "200000 руб."

    vacancy.salary = None
    assert vacancy.salary == "Зарплата не указана"
