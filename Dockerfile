FROM python:3.12.6-bullseye

RUN mkdir /mnt/autocheck

COPY sources.list /etc/apt/sources.list

RUN apt-get update
RUN apt-get install p7zip-full -y
RUN apt-get install unrar -y

COPY autocheck/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY autocheck /test
WORKDIR /test

ENTRYPOINT python3 main.py