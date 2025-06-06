import json


def load_json(path):
    """
    Load JSON data from the specified file path.
    """
    try:
        with open(path, "r", encoding="latin") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON from {path}: {e}")
        return None


def save_json(data, path):
    """
    Save the given data to a JSON file at the specified path.
    """
    try:
        with open(path, "w", encoding="latin") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving JSON to {path}: {e}")
