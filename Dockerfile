FROM python:3.12.6-bullseye

RUN mkdir /mnt/autocheck

COPY autocheck /test
WORKDIR /test

RUN pip install -r requirements.txt

ENTRYPOINT python3 main.py