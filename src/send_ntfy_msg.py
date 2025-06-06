import requests


def send_ntfy_msg(topic, message):
    requests.post(f"https://ntfy.sh/{topic}", data=message.encode(encoding="latin"))


if __name__ == "__main__":
    send_ntfy_msg("NotesUpdate", "fesses")
    print("Message sent successfully.")
