# 🗒️ ECE Grades Extractor

Python scripts to automatically extract and track grades from the ECE student portal.

# ⚙️ Features

- 📊 Extracts grades structured by _Year > Semester > Module > Note Type > Note_ from the ECE grade platform.
- 📝 Generates a JSON file after each extraction.
- 🔄 Automatically compares the latest grades with the previous ones to detect new entries.
- 🧾 Logs detailed changes to help you track your academic progress.

# 💾 Installation

1. Clone the repository

   ```sh
   git clone https://github.com/Alfred0404/ece-grades-extractor.git
   cd ece-grades-extractor
   code .
   ```

2. Install the required dependencies
   ```sh
   pip install requests beautifulsoup4 deepdiff
   ```
3. Build the docker image ([install docker if not already done](https://www.docker.com/products/docker-desktop/))
   ```sh
   docker build -t grades_notifier .
   ```
4. Run your docker container
   ```sh
   docker run grades_notifier
   ```

# 🦾 Future Enhancements

Planned improvements:

- 🕒 Scheduled execution via cron or background service.

# 🤝 Credits

These Python scripts are an adaptation of [BragdonD's original JavaScript project](https://github.com/BragdonD/ECE-Scripts).
Huge thanks to him for the foundational work! 🙌
