import json
from deepdiff import DeepDiff
from utils import load_json
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_diffs(old_file="src/data/notes_old.json", new_file="src/data/notes.json"):
    """
    Compare two JSON files and return the differences.

    @param old_file: Path to the old JSON file.
    @param new_file: Path to the new JSON file.
    @return: A dictionary containing the differences between the two JSON files.
    """
    old_notes = load_json(old_file)
    if old_notes is None:
        raise ValueError(f"Could not load old notes from {old_file}")
    new_notes = load_json(new_file)

    if new_notes is None:
        raise ValueError(f"Could not load new notes from {new_file}")

    diff = DeepDiff(old_notes, new_notes, ignore_order=True)
    return diff


if __name__ == "__main__":
    diffs = get_diffs("src/data/notes_old.json", "src/data/notes.json")
    logging.info(json.dumps(diffs, indent=2, ensure_ascii=False))
