from abc import ABC, abstractmethod
from typing import Dict, List
import requests


class VacancyAPI(ABC):
    """Абстрактный класс для работы с API сервисов вакансий."""

    @abstractmethod
    def connect(self) -> bool:
        """Установить соединение с API."""
        pass

    @abstractmethod
    def get_vacancies(self, query: str, per_page: int = 10) -> List[Dict]:
        """Получить вакансии по запросу."""
        pass


class HeadHunterAPI(VacancyAPI):
    """Реализация API для hh.ru."""

    def __init__(self, base_url: str = "https://api.hh.ru"):
        self._base_url = base_url
        self._session = requests.Session()

    def _connect(self) -> bool:
        """Приватный метод подключения к API."""
        try:
            response = self._session.get(f"{self._base_url}/vacancies")
            return response.status_code == 200
        except requests.RequestException:
            return False

    def connect(self) -> bool:
        return self._connect()

    def get_vacancies(self, query: str, per_page: int = 10) -> List[Dict]:
        """
        Получить вакансии с hh.ru по поисковому запросу.

        Args:
            query: поисковый запрос (например, "Python developer")
            per_page: количество вакансий в ответе (макс. 100)

        Returns:
            Список словарей с данными вакансий
        """
        if not self.connect():
            raise ConnectionError("Не удалось подключиться к API hh.ru")

        params = {
            "text": query,
            "per_page": per_page,
            "page": 0
        }
        try:
            response = self._session.get(
                f"{self._base_url}/vacancies",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            return data.get("items", [])
        except requests.RequestException as e:
            raise ConnectionError(f"Ошибка API: {e}")
