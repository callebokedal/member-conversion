FROM python:3.8-slim-buster

COPY . /usr/src/app
RUN apt-get update \
&& apt-get install gcc -y \
&& apt-get clean

WORKDIR /usr/src/app
RUN pip install --user -r requirements.txt
