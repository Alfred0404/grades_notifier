import os
import time
import logging
from scraper import get_response
from get_grades_diff import get_diffs, parse_diff_details
from send_ntfy_msg import send_ntfy_msg
from utils import load_env_variables, get_env_variable, save_json, load_json
from extract_grades import extract_rows, parse_rows
from setup_logging import setup_logging

MODE = "DEBUG" # Set to "DEBUG" for testing, "PROD" for production
# Set the check interval based on the mode
if MODE == "PROD":
    CHECK_INTERVAL = 10 * 60 # 10 minutes for production

if MODE == "DEBUG":
    CHECK_INTERVAL = 60 # seconds for debugging

setup_logging()
logger = logging.getLogger(__name__)


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
        logger.info("Differences found and old notes updated.")
        notes_json = load_json(current_grades_path)
        diff_details = parse_diff_details(diffs, notes_json)

        logger.info(diff_details)

        # Send a notification with the differences
        for message in diff_details:
            logger.info(f"Sending notification for {message}")
            send_ntfy_msg(topic=topic_name, message=message, redirect_url=redirect_url)
    else:
        logger.info("No differences found.")


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
        logger.info(f"Creating new grades file at {new_grades_path}")
        save_json([], new_grades_path)

    old_grades_path = "src/data/old_grades.json"

    if not os.path.exists(old_grades_path):
        logger.info(f"Creating old grades file at {old_grades_path}")
        save_json([], old_grades_path)

    logger.info("Starting the grades extraction process...")
    while True:

        # Check the current hour
        now = time.localtime()
        current_hour = now.tm_hour
        logger.info(f"Current hour: {current_hour}")

        # If the current hour is between 3 and 5, proceed with the extraction
        if (3 <= current_hour < 5) or MODE == "DEBUG":
            logger.info("hour between 3 n 5 or debug_mode - Fetching grades data...")
            # Sleep for 5 minutes to avoid multiple requests in the same hour

            # Fetch the grades data
            html = get_response(grades_url).text
            rows = extract_rows(html)
            result = parse_rows(rows)

            save_json(result["years"], new_grades_path)
            logger.info("Grades extraction completed and saved to new_grades.json.")

            _ = get_diffs(old_grades_path, new_grades_path)

            compare_and_upgrade_grades(
                old_grades_path, new_grades_path, result["years"], grades_url, topic_name
            )
            logger.info(f"Waiting for {CHECK_INTERVAL} seconds before the next check...")
            time.sleep(CHECK_INTERVAL)
        else:
            logger.info(f"Current hour is not between 3 and 5. Waiting for {CHECK_INTERVAL} seconds before the next check...")
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
