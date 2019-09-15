FROM tiangolo/uwsgi-nginx-flask:python3.6

COPY requirements.txt /tmp/

RUN pip install -U pip \
    && pip install -r /tmp/requirements.txt \
    && python3 -m spacy download en

COPY ./app /app
COPY ./data /app/data
EXPOSE 5000
