import requests
import logging
import time
from urllib3.exceptions import NameResolutionError
from requests.exceptions import ConnectionError
from setup_logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

# Headers to mimic a real browser and avoid 403 errors
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Cache-Control": "max-age=0",
}


def get_response(url, max_retries=3, base_delay=5):
    """
    Get the response from a url with retry logic for DNS failures.

    @param url: The URL to fetch the response from.
    @param max_retries: Maximum number of retry attempts for transient errors.
    @param base_delay: Base delay in seconds for exponential backoff.
    @return: response object from requests.get.
    """
    last_exception = None

    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            logger.info(f"Successfully fetched data from {url}")
            return response

        except ConnectionError as e:
            last_exception = e
            # Check if it's a DNS resolution error
            if "Failed to resolve" in str(e) or "NameResolutionError" in str(e):
                delay = base_delay * (2**attempt)  # Exponential backoff
                logger.warning(
                    f"DNS resolution failed for {url} (attempt {attempt + 1}/{max_retries}). "
                    f"Retrying in {delay} seconds... Error: {e}"
                )
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    continue
                else:
                    logger.error(f"DNS resolution failed after {max_retries} attempts")
            else:
                # Non-DNS connection error, don't retry
                logger.error(f"Connection error while fetching data: {e}")
                raise RuntimeError(f"Connection error while fetching data: {e}")

        except requests.Timeout as e:
            last_exception = e
            logger.error(f"Request timeout while fetching data: {e}")
            raise RuntimeError(f"Request timeout while fetching data: {e}")

        except requests.HTTPError as e:
            last_exception = e
            logger.error(f"HTTP error while fetching data: {e}")
            raise RuntimeError(f"HTTP error while fetching data: {e}")

        except requests.RequestException as e:
            last_exception = e
            logger.error(f"Request error while fetching data: {e}")
            raise RuntimeError(f"Request error while fetching data: {e}")

    # If we exhausted all retries
    raise RuntimeError(
        f"Failed to fetch data after {max_retries} attempts. "
        f"Last error: {last_exception}"
    )
