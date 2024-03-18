from datetime import datetime
import os
import logging

import requests
from requests.adapters import HTTPAdapter
from dotenv import load_dotenv
from urllib3.util import Retry

from constants import DATE_THRESHOLD, RETRY_STATUS_CODES, RETRY_BACKOFF_FACTOR, TOTAL_RETRIES

load_dotenv()

base_url = os.getenv('BASE_URL')
api_key = os.getenv('API_KEY')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_data(url: str, session: requests.Session):
    """
    Fetches data from the provided URL using a specified session.

    :param url: The URL to fetch data from.
    :param session: The requests.Session object to use for the request.
    :return: The fetched data as a JSON object.
    """
    response = session.get(url, headers={'x-api-key': api_key})
    if not response.ok:
        logger.error(f"Error occurred while fetching data from {url}"
                     f"Error: {response.text}"
                     f"Status code: {response.status_code}")
        response.raise_for_status()
    data = response.json()
    logger.info(f"Fetched data from {url}. Response data: {data}")
    return data


def save_outages(url: str, outages: list[dict], session: requests.Session):
    """
    :param url: The URL endpoint where the outages will be saved to.
    :param outages: A list of dictionaries representing the outages to be saved.
    :param session: A `requests.Session` object used to make the HTTP request.
    :return: None
    """
    response = session.post(url, json=outages, headers={'x-api-key': api_key})
    if not response.ok:
        logger.error(f"Error occurred while saving outages to {url}"
                     f"Error: {response.text}"
                     f"Status code: {response.status_code}")
        response.raise_for_status()
    logger.info(f"Outages: {outages} - saved to {url}")


def get_session_with_retry() -> requests.Session:
    """
    Returns a session object that uses a retry strategy for HTTP requests.

    :return: A session object with retry strategy for HTTP requests.
    :rtype: requests.Session
    """
    session = requests.Session()
    retry_strategy = Retry(
        total=TOTAL_RETRIES,
        backoff_factor=RETRY_BACKOFF_FACTOR,
        status_forcelist=RETRY_STATUS_CODES,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    return session


def convert_string_to_date(date: str) -> datetime:
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")


def filter_outages(outages: list[dict], site_info: dict) -> list[dict]:
    """
    Filter outages based on site information.

    :param outages: A list of outage dictionaries.
    :param site_info: A dictionary containing site information.
    :return: A list of filtered outage dictionaries.

    The method filters outages based on the site information provided.
    It compares the begin date of each outage with a low threshold date.
    Only outages with a begin date greater than or equal to the threshold date and
    whose IDs match devices in the site information are included in the filtered outages.
    """
    logger.info(f"Filtering outages by site info")
    filtered_outages = []
    low_threshold = convert_string_to_date(DATE_THRESHOLD)
    devices = {device['id']: device['name'] for device in site_info['devices']}
    for outage in outages:
        begin_date = convert_string_to_date(outage['begin'])
        if begin_date >= low_threshold and outage['id'] in devices:
            filtered_outages.append({
                "id": outage['id'],
                "name": devices[outage['id']],
                "begin": outage['begin'],
                "end": outage['end']
            })
    logger.info(f"Filtered outages: {filtered_outages}")
    return filtered_outages


def run():
    session = get_session_with_retry()
    outages = fetch_data(f'{base_url}/outages', session)
    site_info = fetch_data(f'{base_url}/site-info/norwich-pear-tree', session)
    filtered_outages = filter_outages(outages, site_info)
    save_outages(f'{base_url}/site-outages/norwich-pear-tree', filtered_outages, session)


if __name__ == '__main__':
    run()
