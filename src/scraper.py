import requests
import os
from utils import save_file, load_env_variables

load_env_variables()

ajax_url = os.getenv("GRADES_URL")

if not ajax_url:
    raise ValueError("GRADES_URL environment variable is not set.")

dom_file = "src/data/last_dom.txt"


def get_response(url=ajax_url):
    """
    Get the response.txt from a url.

    @param url: The URL to fetch the response from.
    @return: response object from requests.get.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        raise RuntimeError(f"Error while fetching data : {e}")


def get_dom(ajax_url=ajax_url, dom_file="src/data/last_dom.txt"):
    """
    Scrape the notes from the INSEEC website and return the HTML content.

    @param ajax_url: The URL to fetch the notes from.
    @param dom_file: The file path where the DOM will be saved.
    @raises RuntimeError: If there is an error while fetching the DOM.
    """
    try:
        # Get the current DOM
        dom = get_response(ajax_url).text
        if not dom:
            raise ValueError(
                "The response from the server is empty. Please check the URL or your internet connection."
            )
    except requests.RequestException as e:
        raise RuntimeError(f"Error while getching the DOM : {e}")

    # save the DOM to a .txt file
    save_file(dom, dom_file)
