FROM python:3-slim-buster

COPY ["requirements.txt", "requirements.in", "/usr/src/app/"]
RUN apt-get update \
    && apt-get install gcc -y --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
#RUN pip install --user -r requirements.txt
RUN pip install -r requirements.txt

RUN useradd --create-home --no-log-init --shell /bin/bash --uid 1001 me
USER me
COPY . /home/me
WORKDIR /home/me
