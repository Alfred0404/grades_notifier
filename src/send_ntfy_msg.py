import requests


def send_ntfy_msg(topic, message):
    requests.post(
        f"https://ntfy.sh/{topic}",
        data=message.encode(encoding="latin"),
        headers={
            "Tags": "face_in_clouds",
            "Title": "Nouvelle Note !",
            "Priority": "5",
            "Click": "https://campusonline.inseec.net/note/note.php?AccountName=0%2BHIsIomHaMXLccdGi6GmWIfC2E1e%2BWv3lbOOw%2FzJoQ%3D&couleur=VERT",
        },
    )


if __name__ == "__main__":
    send_ntfy_msg("NotesUpdate", "fesses")
    print("Message sent successfully.")
