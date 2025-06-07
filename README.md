# 🗒️ ECE Grades Extractor

Python scripts to automatically extract and track your grades from the ECE student website.

# ⚙️ Features

- 📊 Extracts structured grades from the ECE platform as:
  _Year → Semester → Module → Note Type → Grade_
- 📝 Outputs a JSON file after each extraction.
- 🔍 Detects new grades by comparing the latest and previous files.
- 📱 Push notifications to keep you informed

# 💾 Installation

The following steps detail the setup I used on a **Raspberry Pi 3 B+** via SSH. You can adapt these instructions to your own server or environment.

### 1. Clone the repository
   ```bash
   git clone https://github.com/Alfred0404/ece-grades-extractor.git
   cd ece-grades-extractor
   code .
   ```

### 2. Install Python dependencies
   ```bash
   pip install requests beautifulsoup4 deepdiff dotenv
   ```

## 📱Setup ntfy

ntfy is a free push notifications service that allows you to send messages to a sub (pub/sub system)

1. Install ntfy on your phone
2. Create your topic and give it a name
3. In your `.env` file (in root), add a `NTFY_TOPIC` variable, set to your topic name

## 🐳 Optional: Deploy with Docker

If you'd like to run the script continuously on a server _(e.g. your Raspberry Pi)_, here’s how to build and deploy the project using Docker.

### 3. Install Docker on your local machine

Download from [docker.com](https://www.docker.com/products/docker-desktop/) if not already installed.

### 4. Install Docker on the Raspberry Pi
   ```
   curl -sSL https://get.docker.com | sh
   sudo usermod -aG docker pi
   ```
    ℹ️ Log out and log back in (or reboot) for the group change to apply

### 5. Pull the docker image

   Go check the [package](https://github.com/Alfred0404/notes_scraping/pkgs/container/grades_notifier) and their pull commands
   ```bash
   docker pull ghcr.io/alfred0404/grades_notifier:<your_architecture>
   ```
### 6. create a `docker-compose.yml` file
   It is important to environment variables in your docker compose file.

   ```bash
   version: "3.8"

   services:
   grades_notifier:
      image: ghcr.io/alfred0404/grades_notifier:armv7
      dns:
         - 8.8.8.8
      container_name: grades_notifier_container
      restart: unless-stopped
      environment:
         - GRADES_URL=your_url
         - CLICK_GRADES_URL=the_url_you_want_to_be_redirected_to
         - NTFY_TOPIC=your_topic
      command: python src/main.py
   ```

### 6. Run the image
   ```bash
   docker compose up -d
   ```

🎉 The image should now run.

# 🔒 ENV Variables
| Variable         | Default                                                                                                                                | Description                             |
|-------------------|----------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------|
| GRADES_URL       | `https://campusonline.inseec.net/note/note_ajax.php?AccountName=<your_account>_id&c=classique&mode_affichage=&version=PROD&mode_test=N` | Url the script scrap from               |
| CLICK_GRADES_URL | `https://campusonline.inseec.net/note/note.php?AccountName=<your_account_id>&couleur=VERT`                                              | The url you will be redirected to when clicking on the ntfy notification |
| NTFY_TOPIC       | `<your_ntfy_topic_name>`                                                                                                                 | Your topic name, that must be the same as the one you created on your phone |

# 🤝 Credits

This project is based on [BragdonD's](https://github.com/BragdonD/ECE-Scripts/tree/main) original JavaScript project.

Huge thanks to him for laying the foundation! 🙌