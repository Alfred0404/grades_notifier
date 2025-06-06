import json
from deepdiff import DeepDiff
from utils import load_json


def get_diffs(old_file="notes_old.json", new_file="notes.json"):
    """
    Compare two JSON files and return the differences.
    """
    old_notes = load_json(old_file)
    if old_notes is None:
        raise ValueError(f"Could not load old notes from {old_file}")
    nex_notes = load_json(new_file)
    if nex_notes is None:
        raise ValueError(f"Could not load new notes from {new_file}")

    diff = DeepDiff(old_notes, nex_notes, ignore_order=True)
    return diff

if __name__ == "__main__":
    diffs = get_diffs("src/notes_old.json", "src/notes.json")
    print(json.dumps(diffs, indent=2, ensure_ascii=False))