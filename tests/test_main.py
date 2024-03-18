from datetime import datetime

import pytest
import requests
from unittest.mock import patch, Mock
from main import fetch_data, save_outages, convert_string_to_date, filter_outages
from tests.conftest import MOCK_API_KEY


@patch("requests.Session.get")
def test_fetch_data_success(mock_get):
    mock_get.return_value.ok = True
    mock_get.return_value.json.return_value = "data"
    result = fetch_data("http://test.url", requests.Session())
    assert result == "data"


@patch("requests.Session.get")
def test_fetch_data_failure(mock_get):
    mock_get.return_value.ok = False
    mock_get.return_value.status_code = 404
    mock_get.return_value.text = "Not Found"
    mock_get.return_value.raise_for_status.side_effect = requests.HTTPError
    with pytest.raises(requests.exceptions.HTTPError):
        fetch_data("http://test.url", requests.Session())


@patch('requests.Session')
@patch('main.logger')
def test_save_outages_success(mock_logger, mock_session):
    mock_response = Mock()
    mock_response.ok = True
    mock_session.post.return_value = mock_response

    save_outages('http://test.url', [{'id': 1}], mock_session)

    mock_session.post.assert_called_once_with(
        'http://test.url',
        json=[{'id': 1}],
        headers={'x-api-key': MOCK_API_KEY}
    )

    assert mock_logger.error.call_count == 0
    mock_logger.info.assert_called_once()


@patch('requests.Session')
@patch('main.logger')
def test_save_outages_error(mock_logger, mock_session):
    mock_response = Mock()
    mock_response.ok = False
    mock_response.text = "Error Text"
    mock_response.status_code = 400
    mock_response.raise_for_status.side_effect = requests.HTTPError
    mock_session.post.return_value = mock_response

    with pytest.raises(requests.HTTPError):
        save_outages('http://test.url', [{'id': 1}], mock_session)

    mock_session.post.assert_called_once_with(
        'http://test.url',
        json=[{'id': 1}],
        headers={'x-api-key': MOCK_API_KEY}
    )

    mock_logger.error.assert_called_once()
    assert mock_logger.info.call_count == 0


def test_convert_string_to_date():
    assert convert_string_to_date("2020-01-01T00:00:00.000Z") == datetime(2020, 1, 1)
    assert convert_string_to_date("2023-12-31T23:59:59.999Z") == datetime(2023, 12, 31, 23, 59, 59, 999000)
    assert convert_string_to_date("1970-01-01T00:00:00.000Z") == datetime(1970, 1, 1)


def test_filter_outages_no_matching_ids():
    outages = [{'id': 'CCC', 'begin': '2022-06-07T16:54:10.037Z', 'end': '2022-06-27T00:33:38.078Z'},
               {'id': 'DDD', 'begin': '2022-01-28T04:47:58.093Z', 'end': '2022-08-10T10:56:18.343Z'}]

    site_info = {'devices': [{'id': 'AAA', 'name': 'Device_AAA'}, {'id': 'BBB', 'name': 'Device_BBB'}]}

    filtered = filter_outages(outages, site_info)
    assert filtered == []


def test_filter_outages_with_match():
    outages = [{'id': 'AAA', 'begin': '2022-06-07T16:54:10.037Z', 'end': '2022-06-27T00:33:38.078Z'},
               {'id': 'BBB', 'begin': '2020-06-07T16:54:10.037Z', 'end': '2020-06-27T00:33:38.078Z'},
               {'id': 'DDD', 'begin': '2021-06-07T16:54:10.037Z', 'end': '2021-06-27T00:33:38.078Z'}]

    site_info = {'devices': [{'id': 'AAA', 'name': 'Device_AAA'}, {'id': 'BBB', 'name': 'Device_BBB'}]}

    expected = [
        {
            'id': 'AAA',
            'name': 'Device_AAA',
            'begin': '2022-06-07T16:54:10.037Z',
            'end': '2022-06-27T00:33:38.078Z'
        }
    ]

    filtered = filter_outages(outages, site_info)
    assert filtered == expected


def test_filter_outages_site_info_low_threshold():
    outages = [{'id': 'AAA', 'begin': '2020-06-07T16:54:10.037Z', 'end': '2020-06-27T00:33:38.078Z'}]
    site_info = {'devices': [{'id': 'AAA', 'name': 'Device_AAA'}, {'id': 'BBB', 'name': 'Device_BBB'}]}

    filtered = filter_outages(outages, site_info)
    assert filtered == []
