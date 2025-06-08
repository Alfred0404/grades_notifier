import json
import os
import logging
from scraper import get_response
from get_grades_diff import get_diffs, parse_diff_details
from send_ntfy_msg import send_ntfy_msg
from utils import load_env_variables, get_env_variable, save_json, load_json
from extract_grades import extract_rows, parse_rows

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def compare_and_upgrade_grades(
    old_grades_path, current_grades_path, data, redirect_url, topic_name
):
    """
    Compare the old and new grades, update the old grades file if there are differences,
    and send a notification with the differences.

    @param old_grades_path: Path to the old grades JSON file.
    @param current_grades_path: Path to the current grades JSON file.
    @param data: The extracted grades data to save if differences are found.
    """
    # Get the differences between the old and new notes
    diffs = get_diffs(old_grades_path, current_grades_path)

    # Print the differences
    if diffs:
        # Update the old notes file with the new notes
        save_json(data, old_grades_path)
        logging.info("Differences found and old notes updated.\n")
        notes_json = load_json(current_grades_path)
        diff_details = parse_diff_details(diffs, notes_json)

        # Send a notification with the differences
        for message in diff_details:
            send_ntfy_msg(topic=topic_name, message=message, redirect_url=redirect_url)
    else:
        logging.info("No differences found.\n")


def main():
    load_env_variables()

    topic_name = get_env_variable("NTFY_TOPIC")

    if not topic_name:
        raise ValueError("NTFY_TOPIC environment variable is not set.")

    grades_url = get_env_variable(f"GRADES_URL")

    if not grades_url:
        raise ValueError("GRADES_URL environment variable is not set.")

    new_grades_path = "src/data/new_grades.json"

    if not os.path.exists(new_grades_path):
        logging.info(f"Creating new grades file at {new_grades_path}")
        save_json([], new_grades_path)

    old_grades_path = "src/data/old_grades.json"

    if not os.path.exists(old_grades_path):
        logging.info(f"Creating old grades file at {old_grades_path}")
        save_json([], old_grades_path)

    logging.info("Starting the grades extraction process...")
    html = get_response(grades_url).text
    rows = extract_rows(html)
    result = parse_rows(rows)

    save_json(result["years"], new_grades_path)
    logging.info("Grades extraction completed and saved to new_grades.json.")

    diffs = get_diffs(old_grades_path, new_grades_path)
    logging.info(json.dumps(diffs, indent=4, ensure_ascii=False))

    compare_and_upgrade_grades(
        old_grades_path, new_grades_path, result["years"], grades_url, topic_name
    )


if __name__ == "__main__":
    main()
