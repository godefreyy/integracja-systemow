FROM python:3.12-slim

WORKDIR /srv/app

# install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy source
COPY app ./app

# default entrypoint – flask dev server (good enough for demo / labs)
ENV FLASK_APP=app:create_app
CMD ["flask", "run", "--host=0.0.0.0"]
