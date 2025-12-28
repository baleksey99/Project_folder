import json
from abc import ABC, abstractmethod
from typing import List, Optional


class JSONSaver(ABC):
    @abstractmethod
    def add_vacancy(self, vacancy):
        pass

    @abstractmethod
    def delete_vacancy(self, vacancy_url: str) -> bool:
        pass  # Только объявление — реализация в наследнике


class ConcreteJSONSaver(JSONSaver):
    def __init__(self, filepath: str):
        self.filepath = filepath

    def add_vacancy(self, vacancy) -> None:
        data = self._load_data()
        data.append(vacancy)
        self._save_data(data)

    def delete_vacancy(self, vacancy_url: str) -> bool:
        """Удалить вакансию по URL. Возвращает True, если вакансия была найдена и удалена."""
        data = self._load_data()
        filtered_data = [item for item in data if item["url"] != vacancy_url]

        if len(filtered_data) < len(data):
            self._save_data(filtered_data)
            return True  # Явно возвращаем True при успешном удалении
        return False  # Вакансия не найдена

    def get_vacancies(self, keyword: Optional[str] = None) -> List[dict]:
        data = self._load_data()
        if not keyword:
            return data
        filtered = []
        for item in data:
            if (keyword.lower() in item["title"].lower() or keyword.lower() in item["description"].lower()):
                filtered.append(item)
        return filtered

    def _load_data(self) -> List[dict]:
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_data(self, data: List[dict]) -> None:
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
