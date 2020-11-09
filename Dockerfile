FROM python:3.8-slim-buster

# RUN groupadd -r myuser && useradd -r -g myuser myuser

COPY . /usr/src/app
RUN apt-get update \
&& apt-get install gcc -y \
&& apt-get clean

# USER myuser
WORKDIR /usr/src/app
RUN pip install --user -r requirements.txt
#ENTRYPOINT uvicorn main:app --reload --host 0.0.0.0 --port 8080

