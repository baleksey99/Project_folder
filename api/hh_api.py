from typing import Dict, List
import requests


class HeadHunterAPI:
    """Клиент для работы с API hh.ru."""

    def __init__(self, base_url: str = "https://api.hh.ru"):
        self.base_url = base_url
        self.session = requests.Session()

    def get_employer_info(self, employer_id: int) -> Dict:
        """Получить информацию о компании."""
        url = f"{self.base_url}/employers/{employer_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_company_vacancies(self, employer_id: int, per_page: int = 100) -> List[Dict]:
        """Получить вакансии компании."""
        url = f"{self.base_url}/vacancies"
        params = {"employer_id": employer_id, "per_page": per_page}
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json().get("items", [])

    def get_vacancies(self, query: str, area: int = None, per_page: int = 20) -> List[Dict]:
        """
        Получить вакансии по поисковому запросу.

        :param query: поисковый запрос (например, 'Python разработчик')
        :param area: ID региона (по умолчанию None — все регионы)
        :param per_page: количество вакансий на страницу
        :return: список вакансий
        """
        url = f"{self.base_url}/vacancies"
        params = {
            "text": query,
            "area": area,
            "per_page": per_page
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json().get("items", [])
