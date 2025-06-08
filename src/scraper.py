import requests
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_response(url):
    """
    Get the response.txt from a url.

    @param url: The URL to fetch the response from.
    @return: response object from requests.get.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        logging.info(f"Successfully fetched data from {url}")
        return response

    except requests.RequestException as e:
        raise RuntimeError(f"Error while fetching data : {e}")
