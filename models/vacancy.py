import re
from functools import total_ordering
from typing import Dict, Optional


@total_ordering
class Vacancy:
    def __init__(self, title: str, url: str, salary: Optional[str] = None, description: str = ""):
        self._title = self._validate_title(title)
        self._url = self._validate_url(url)
        self._salary = self._validate_salary(salary)
        self._description = description.strip()

    def to_dict(self) -> dict:
        """Преобразовать объект Vacancy в словарь для JSON-сериализации."""
        return {
            "title": self._title,
            "url": self._url,
            "salary": self._salary,
            "description": self._description
        }

    def _is_valid_url(self, url: str) -> bool:
        """Проверяет корректность URL"""
        return isinstance(url, str) and (
            url.startswith("http://")
            or url.startswith("https://")
        )

    def _validate_title(self, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Название вакансии не может быть пустым")
        return value.strip()

    def _validate_url(self, value: str) -> str:
        if not value:
            raise ValueError("URL вакансии не может быть пустым")
        if not re.match(r"^https?://", value):
            raise ValueError("Некорректный формат URL")
        return value

    def _validate_salary(self, value: Optional[str]) -> str:
        if value is None or not value.strip():
            return "Зарплата не указана"
        # Нормализуем: убираем пробелы в числах
        normalized = re.sub(r"(\d)\s+(\d)", r"\1\2", value.strip())
        return normalized

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str):
        self._title = self._validate_title(value)

    @property
    def url(self) -> str:
        return self._url

    @url.setter
    def url(self, value: str):
        self._url = self._validate_url(value)

    @property
    def salary(self) -> str:
        return self._salary

    @salary.setter
    def salary(self, value: Optional[str]):
        self._salary = self._validate_salary(value)

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value.strip()

    def get_salary_value(self) -> Optional[int]:
        """Извлечь числовое значение зарплаты (нижняя граница)."""
        if self._salary == "Зарплата не указана":
            return None
        numbers = re.findall(r"\d+", self._salary)
        return int(numbers[0]) if numbers else None

    def __eq__(self, other) -> bool:
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self.get_salary_value() == other.get_salary_value()

    def __lt__(self, other) -> bool:
        if not isinstance(other, Vacancy):
            return NotImplemented

        this_salary = self.get_salary_value()
        other_salary = other.get_salary_value()

        # Если у текущей вакансии зарплата не указана, она меньше любой с указанной зарплатой
        if this_salary is None:
            return other_salary is not None  # True, если у other зарплата есть
        # Если у other зарплата не указана, текущая больше
        if other_salary is None:
            return False
        # Обычное сравнение чисел
        return this_salary < other_salary

    def to_dicts(self) -> Dict:
        """Преобразовать вакансию в словарь для сохранения."""
        return {
            "title": self._title,
            "url": self._url,
            "salary": self._salary,
            "description": self._description
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Vacancy':
        """Создать вакансию из словаря."""
        return cls(
            title=data["title"],
            url=data["url"],
            salary=data.get("salary"),
            description=data.get("description", "")
        )

    def __str__(self) -> str:
        return f"{self._title} — {self._salary} ({self._url})"
