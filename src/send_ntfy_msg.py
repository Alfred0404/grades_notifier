import requests
import os
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
from utils import load_env_variables

load_env_variables()

grades_url = os.getenv("CLICK_GRADES_URL")
ntfy_topic = os.getenv("NTFY_TOPIC")


def send_ntfy_msg(topic, message, redirect_url):
    """
    Send a notification message to the specified ntfy topic.

    @param topic: The ntfy topic to send the message to.
    @param message: The message to send.
    """
    try:
        response = requests.post(
            f"https://ntfy.sh/{topic}",
            data=message.encode(encoding="latin"),
            headers={
                "Tags": "face_in_clouds",
                "Title": "Nouvelle Note !",
                "Priority": "5",
                "Click": redirect_url,
            },
        )
        response.raise_for_status()
        logging.info(f"Sending {message} to topic {topic}")
    except Exception as e:
        logging.error(f"Failed to send ntfy message: {e}")


if __name__ == "__main__":
    try:
        send_ntfy_msg(ntfy_topic, "bogos binted")
        logging.info("Notification sent successfully.")

    except Exception as e:
        logging.error(f"Failed to send notification: {e}")
