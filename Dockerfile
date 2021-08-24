FROM python:3.9.6-slim

RUN pip install --upgrade pip 'poetry==1.1.6'

ARG uid=1000

RUN adduser -u ${uid} --disabled-password --disabled-login --gecos python python
USER python

WORKDIR /srv
COPY poetry.lock pyproject.toml /srv/
RUN poetry install
COPY binance/ /srv/
ENTRYPOINT ["poetry", "run", "python", "main.py"]
CMD ["--data", "q1"]