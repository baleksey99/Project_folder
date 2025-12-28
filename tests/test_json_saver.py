import os


def test_json_saver_add_vacancy(json_saver, sample_vacancy):
    json_saver.add_vacancy(sample_vacancy)
    assert os.path.exists(json_saver.filepath)


def test_json_saver_get_vacancies_by_filter(json_saver, sample_vacancies):
    for v in sample_vacancies:
        json_saver.add_vacancy(v)
    filtered = json_saver.get_vacancies(keyword="Django")
    assert len(filtered) > 0


def test_json_saver_delete_vacancy(json_saver, sample_vacancy):
    # 1. Добавляем вакансию
    json_saver.add_vacancy(sample_vacancy)

    # 2. Удаляем по URL
    deleted = json_saver.delete_vacancy(sample_vacancy.url)

    # 3. Проверяем, что метод вернул True
    assert deleted is True
