import requests
import logging
from setup_logging import setup_logging
setup_logging()
logger = logging.getLogger(__name__)


def get_response(url):
    """
    Get the response.txt from a url.

    @param url: The URL to fetch the response from.
    @return: response object from requests.get.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        logger.info(f"Successfully fetched data from {url}")
        return response

    except requests.RequestException as e:
        raise RuntimeError(f"Error while fetching data : {e}")
