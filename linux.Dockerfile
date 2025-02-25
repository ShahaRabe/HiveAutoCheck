FROM python:3.12.6-bullseye

RUN mkdir /mnt/autocheck

COPY sources.list /etc/apt/sources.list

RUN apt-get update
RUN apt-get install -y p7zip-full unrar
RUN apt-get install -y cmake clang 

COPY autocheck/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY ./dist/*.whl /tmp/
RUN python3 -m pip install /tmp/*.whl

COPY autocheck /test
WORKDIR /

ENTRYPOINT python3 -m test