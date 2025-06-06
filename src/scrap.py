import requests
from dotenv import load_dotenv
import os

if os.path.exists(".env"):
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        print("dotenv module not found, skipping .env loading")

ajax_url = os.getenv("GRADES_URL")

if not ajax_url:
    raise ValueError("GRADES_URL environment variable is not set.")

dom_file = "src/last_dom.txt"


def get_dom(ajax_url=ajax_url, dom_file="src/last_dom.txt"):
    """
    Scrape the notes from the INSEEC website and return the HTML content.
    """
    try:
        # Récupérer le DOM actuel
        response = requests.get(ajax_url, timeout=10)
        response.raise_for_status()
        dom = response.text
        if not dom:
            raise ValueError(
                "Le DOM est vide. Vérifiez l'URL ou la connexion Internet."
            )
    except requests.RequestException as e:
        raise RuntimeError(f"Erreur lors de la récupération du DOM : {e}")

    try:
        # Enregistrer le DOM dans un fichier
        with open(dom_file, "w", encoding="latin") as f:
            f.write(dom)
    except OSError as e:
        raise RuntimeError(f"Erreur lors de l'écriture du fichier DOM : {e}")
