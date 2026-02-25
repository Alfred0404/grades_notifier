#!/bin/sh
# Start the grades scraper in the background
python src/main.py &

# Start the web UI (foreground, so Docker tracks the process)
exec python -m uvicorn src.web.api:app --host 0.0.0.0 --port 8000
