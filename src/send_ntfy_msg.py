import requests
from dotenv import load_dotenv
import os

if os.path.exists(".env"):
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        print("dotenv module not found, skipping .env loading")

grades_url = os.getenv("CLICK_GRADES_URL")
ntfy_topic = os.getenv("NTFY_TOPIC")

def send_ntfy_msg(topic, message):
    requests.post(
        f"https://ntfy.sh/{topic}",
        data=message.encode(encoding="latin"),
        headers={
            "Tags": "face_in_clouds",
            "Title": "Nouvelle Note !",
            "Priority": "5",
            "Click": grades_url,
        },
    )
    print(f"Sending {message} to topic {topic}")


if __name__ == "__main__":
    try:
        send_ntfy_msg(ntfy_topic, "fesses")
        print("Message sent successfully.")
    except Exception as e:
        print(f"Failed to send message: {e}")
