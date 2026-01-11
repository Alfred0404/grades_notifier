import requests
import logging
from setup_logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://campusonline.inseec.net/note/note.php",
}


def get_response(url: str) -> requests.Response:
    """
    Get the response from a URL.

    Args:
        url (str): The URL to fetch.
    Returns:
        requests.Response: The HTTP response object.
    """

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        logger.info("Successfully fetched data")

        return response

    except requests.RequestException as e:
        logger.error("HTTP error while fetching data", exc_info=e)

        raise RuntimeError(f"Error while fetching data: {e}")
