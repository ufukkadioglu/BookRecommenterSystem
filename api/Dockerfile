FROM python:3.10.6-slim-buster

WORKDIR /api

RUN apt update --fix-missing

# install c compiler
RUN apt install gcc -y

# copy project files
COPY . .

# install requirements
RUN pip install -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/api"

# start api
CMD exec uwsgi --socket 0.0.0.0:80 --protocol=http -w wsgi:app
