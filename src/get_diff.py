import json
from deepdiff import DeepDiff


def get_diffs(old_file="notes_old.json", new_file="notes.json"):
    """
    Compare two JSON files and return the differences.
    """
    with open(old_file, "r", encoding="latin") as f:
        old_notes = json.load(f)
    with open(new_file, "r", encoding="latin") as f:
        nex_notes = json.load(f)

    diff = DeepDiff(old_notes, nex_notes, ignore_order=True)
    return diff

if __name__ == "__main__":
    diffs = get_diffs("src/notes_old.json", "src/notes.json")
    print(json.dumps(diffs, indent=2, ensure_ascii=False))