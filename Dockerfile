FROM tiangolo/uwsgi-nginx-flask:python3.6

COPY requirements.txt /tmp/

RUN pip install -U pip \
    && pip install -r /tmp/requirements.txt \
    && pip install -U spacy==2.0.3 \
    && python3 -m spacy download en \
    && python3 -m spacy download xx

COPY ./app /app
EXPOSE 5000
