import requests

ajax_url = "https://campusonline.inseec.net/note/note_ajax.php?AccountName=0%2BHIsIomHaMXLccdGi6GmWIfC2E1e%2BWv3lbOOw%2FzJoQ%3D&c=classique&mode_affichage=&version=PROD&mode_test=N"
dom_file = "src/last_dom.txt"


def get_dom(ajax_url=ajax_url, dom_file="src/last_dom.txt"):
    """
    Scrape the notes from the INSEEC website and return the HTML content.
    """
    # Récupérer le DOM actuel
    response = requests.get(ajax_url)
    dom = response.text
    if not dom:
        raise ValueError("Le DOM est vide. Vérifiez l'URL ou la connexion Internet.")

    # Enregistrer le DOM dans un fichier
    with open(dom_file, "w", encoding="latin") as f:
        f.write(dom)
