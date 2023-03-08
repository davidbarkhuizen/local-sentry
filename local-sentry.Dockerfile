FROM python:3.10

ENV POETRY_VERSION=1.2.0
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv
ENV POETRY_CACHE_DIR=/opt/.cache
ENV LOCAL_SENTRY_PORT=9000

RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

RUN poetry config 

# line belows fails with error "/app/local_sentry does not contain any element" if it is not run with --no-root
RUN poetry install --no-interaction --no-ansi --no-root

COPY . /app

CMD [ "poetry", "run", "python", "local_sentry/local_sentry.py" ]