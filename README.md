<div align="center">

# **Grades Notifier**

_**Get notified when a new grade pop**_

</div>

<details>
    <summary>📖 Table of content</summary>
    <ol>
        <li><a href="#introduction">☝️ Introduction</a></li>
        <li><a href="#features">⚙️ Features</a></li>
        <li><a href="#structure">🏗️ Structure</a></li>
        <li><a href="#installation">💾 Installation</a></li>
        <li><a href="#docker">🐳 Docker</a></li>
        <li><a href="#env-variables">🔒 ENV Variables</a></li>
        <li><a href="#contribute">🤝 Contribute</a></li>
    </ol>
</details>

# ☝️ Introduction

As ECE doesn't provide any notification system for grades, I decided to code my own notification system.
Grades Notifier is a lightweight Python tool that monitors your ECE student portal for new grades and instantly sends a push notification to your phone using [ntfy.sh](https://ntfy.sh).

# ⚙️ Features

- 📊 Extracts structured grades from the ECE platform as:
  _Year → Semester → Module → Note Type → Grade_
- 📝 Outputs a JSON file after each extraction.
- 🔍 Detects new grades by comparing the latest and previous files.
- 📱 Push notifications to keep you informed

# 🏗️ Structure

```bash
grades_notifier
├── src
│   ├── data
│   │   └── new_grades.json
│   │   └── old_grades.json
│   ├── extract_grades.py
│   ├── get_grades_diff.py
│   ├── main.py
│   ├── scraper.py
│   ├── send_ntfy_msg.py
│   └── utils.py
├── .dockerignore
├── .env
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
```

# Prerequisite

Before starting, ensure to have these installed on your machine
- [Python 3.8 +](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installation/)
- [Docker](https://www.docker.com/products/docker-desktop/) _(if you plan to use it)_

# Usage

Run locally
```bash
python src/main.py
```

# 💾 Installation

The following steps detail the setup I used on a **Raspberry Pi 3 B+** via SSH. You can adapt these instructions to your own server or environment.

### 1. Clone the repository

```bash
git clone https://github.com/Alfred0404/grades_notifier.git
cd grades_notifier
code .
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

## 📱Setup ntfy

ntfy is a free notifications service that allows you to send messages to a sub (pub/sub system).

1. Install ntfy on your phone
2. Create your topic and give it a name
3. In your `.env` file (in root), add a `NTFY_TOPIC` variable, set to your topic name

## 🐳 Optional: Deploy with Docker

If you'd like to run the script continuously on a server _(e.g. your Raspberry Pi)_, here’s how to build and deploy the project using Docker.

### 3. Install Docker on your local machine

Download from [docker.com](https://www.docker.com/products/docker-desktop/) if not already installed.

### 4. Install Docker on the Raspberry Pi

```sh
curl -sSL https://get.docker.com | sh
sudo usermod -aG docker pi
```

    ℹ️ Log out and log back in (or reboot) for the group change to apply

### 5. Pull the docker image

Check the [package](https://github.com/Alfred0404/notes_scraping/pkgs/container/grades_notifier) for pull commands.

```bash
docker pull ghcr.io/alfred0404/grades_notifier:<your_architecture>
```

Run `uname -a` to know the architecture.

### 6. Create a `docker-compose.yml` file

Ensure to put your environment variables in your `docker-compose/yml` file.

```yml
services:
grades_notifier:
   image: ghcr.io/alfred0404/grades_notifier:armv7
   dns:
      - 8.8.8.8
   container_name: grades_notifier_container
   restart: no
   environment:
      - GRADES_URL=<your_url>
      - CLICK_GRADES_URL=<the_url_you_want_to_be_redirected_to>
      - NTFY_TOPIC=<your_topic>
   command: python src/main.py
```

### 6. Run the image

```bash
docker compose run --rm grades_notifier
```

The container should now run 🎉.

### 7. Create a launch_grades_notifier.sh file

```bash
# launch_grades_notifier exemple
#!/bin/bash

# Stop the script if an error occur
set -e

cd /home/pi/grades_notifier || { echo "Erreur : can't find folder"; exit 1; }

# Run the container and delete it after execution
docker compose run --rm grades_notifier
```

### 8. Setup a cronjob

Cron lets you schedule the container execution

- Run `crontab -e`
- If prompted to select an editor :
  ```bash
  no crontab for pi - using an empty one
  Select an editor. To change later, run 'select-editor'.
  1. /bin/nano
  2. /usr/bin/vim.basic
  3. /bin/ed
  4. /usr/bin/mcedit
  Choose 1-4 [1]:
  ```
  Choose `nano` _(1)_
- Add the following line to your crontab file

```cron
30 7 * * * /home/pi/grades_notifier/launch_grades_notifier.sh >> /home/pi/grades_notifier/cron.log 2>&1
```
- refer to the [cron documentation](https://docs.gitlab.com/topics/cron/) for more details.

Cron should now execute the container everyday at 7:30 am 🎉.

# 🔒 ENV Variables

| Variable         | Description                                                                 | Value                                                                                                                                   |
| ---------------- | --------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| GRADES_URL       | Url the script scrap from                                                   | `https://campusonline.inseec.net/note/note_ajax.php?AccountName=<your_account>_id&c=classique&mode_affichage=&version=PROD&mode_test=N` |
| CLICK_GRADES_URL | The url you will be redirected to when clicking on the ntfy notification    | `https://campusonline.inseec.net/note/note.php?AccountName=<your_account_id>&couleur=VERT`                                              |
| NTFY_TOPIC       | Your topic name, that must be the same as the one you created on your phone | `<your_ntfy_topic_name>`                                                                                                                |

# 🤝 Contribute

Feel free to contribute to this project. Your input is welcome !
