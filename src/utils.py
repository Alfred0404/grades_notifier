import json
import os
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def load_json(path):
    """
    Load JSON data from the specified file path.

    @param path: The file path to load the JSON data from.
    @return: The loaded JSON data as a dictionary or list, or None if an error occurs.
    """
    try:
        with open(path, "r", encoding="latin") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading JSON from {path}: {e}")
        return None


def save_json(data, path):
    """
    Save the given data to a JSON file at the specified path.

    @param data: The data to save, as a dictionary or list.
    @param path: The file path where the JSON data should be saved.
    """
    try:
        with open(path, "w", encoding="latin") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Error saving JSON to {path}: {e}")


def save_file(data, path):
    """
    Save the given data to a file at the specified path.

    @param data: The data to save, as a string.
    @param path: The file path where the data should be saved.
    """
    try:
        with open(path, "w", encoding="latin") as f:
            f.write(data)
    except Exception as e:
        logging.error(f"Error saving file to {path}: {e}")


def load_file(path):
    """
    Load data from a file at the specified path.

    @param path: The file path to load the data from.
    @return: The content of the file as a string, or None if an error occurs.
    """
    try:
        with open(path, "r", encoding="latin") as f:
            return f.read()
    except Exception as e:
        logging.error(f"Error loading file from {path}: {e}")
        return None


def load_env_variables():
    """
    Load environment variables from a .env file if it exists.
    This function attempts to load the dotenv module and load the .env file.
    If the dotenv module is not found, it prints a message and skips loading.
    """
    if os.path.exists(".env"):
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except ImportError:
            logging.warning("dotenv module not found, skipping .env loading")
