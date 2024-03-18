from unittest.mock import patch

import pytest


MOCK_API_KEY = 'mock_api_key'


@pytest.fixture(autouse=True, scope='session')
def mock_env_vars():
    with patch('main.api_key', new=MOCK_API_KEY):
        with patch('main.DATE_THRESHOLD', new='2021-01-01T00:00:00.000Z'):
            yield
