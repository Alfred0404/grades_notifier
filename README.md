# 🗒️ ECE Grades Extractor

Python scripts to automatically extract and track grades from the ECE student portal.
# ⚙️ Features

- 📊 Extracts grades structured by Year > Semester > Module > Note Type > Note from the ECE grade platform.
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

# 🦾 Future Enhancements

Planned improvements:

- ✅ Docker support for easy deployment on a home server (e.g., Raspberry Pi).
- 🕒 Scheduled execution via cron or background service.
- 📬 Email or Telegram notifications for newly posted grades.
- 🖼️ Web interface to visualize grade history.

# 🤝 Credits

These Python scripts are an adaptation of BragdonD's original JavaScript project.
Huge thanks to him for the foundational work! 🙌