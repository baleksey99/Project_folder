import pytest
from requests.exceptions import RequestException


def test_hh_api_connect_success(hh_api, mocker):
    mocker.patch.object(hh_api._session, 'get', return_value=type('Response', (), {'status_code': 200}))
    assert hh_api.connect() is True


def test_hh_api_connect_failure(hh_api, mocker):
    mocker.patch.object(hh_api._session, 'get', side_effect=RequestException)
    assert hh_api.connect() is False


def test_get_vacancies_success(hh_api, mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json = lambda: {
        "items": [
            {"id": "1", "name": "Dev", "salary": {"from": 100000, "to": 150000, "currency": "руб."}},
            {"id": "2", "name": "QA", "salary": None}
        ]
    }

    mocker.patch.object(hh_api._session, 'get', return_value=mock_response)

    vacancies = hh_api.get_vacancies("Python", per_page=2)
    assert len(vacancies) == 2


def test_get_vacancies_connection_error(hh_api, mocker):
    mocker.patch.object(hh_api._session, 'get', side_effect=RequestException)
    with pytest.raises(ConnectionError):
        hh_api.get_vacancies("Python")
