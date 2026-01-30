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

# ⚠️ Prerequisite

Before starting, ensure to have these installed on your machine

- [Python 3.8 +](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installation/)
- [Docker](https://www.docker.com/products/docker-desktop/) _(if you plan to use it)_

# 📡 Usage

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

### 3. Set up environment variables

Copy the `.env.example` file to `.env` and fill in your own values:

```bash
cp .env.example .env
```

Then edit the `.env` file with your specific configuration.

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
docker pull ghcr.io/alfred0404/grades_notifier:latest
```

### 6. Create a `docker-compose.yml` file in the project root

Create a `docker-compose.yml` file in the root directory of the project (`grades_notifier/docker-compose.yml`). Make sure to include your environment variables in this file. See [docker-compose.yml.example](/docker-compose.yml.example) for reference.

```bash
mkdir -p ~/docker/grades_notifier
cd ~/docker/grades_notifier
nano docker-compose.yml
```

### 7. Run the container

```bash
docker compose up -d
```

The container should now be running 🎉
You will receive notifications on your ntfy topic whenever new grades are posted.

To check the real-time output of the Docker container:

```bash
docker compose logs -f grades_notifier
```

## Troubleshooting

The most common errors are related to incorrect URLs. If you encounter a URL-related error, you may need to modify the environment variables in `docker-compose.yml`.

# 🤝 Contribute

Feel free to contribute to this project. Your input is welcome !

<p align="center">
	<img src="https://raw.githubusercontent.com/catppuccin/catppuccin/main/assets/footers/gray0_ctp_on_line.svg?sanitize=true" />
</p>