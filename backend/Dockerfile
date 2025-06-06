FROM python:3.12-slim

WORKDIR /srv/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

ENV FLASK_APP=app:create_app
CMD ["flask", "run", "--host=0.0.0.0"]
