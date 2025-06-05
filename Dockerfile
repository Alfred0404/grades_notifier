FROM python:3.13.3

ADD main.py .

RUN pip install requests beautifulsoup4 deepdiff

CMD ["python", "./main.py"]