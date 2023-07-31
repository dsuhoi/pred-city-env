FROM python:3.10-slim

WORKDIR /backend_app

RUN apt-get update && apt-get install -y libpq-dev netcat
RUN pip3 install poetry

COPY . .

RUN poetry config virtualenvs.create false \
&& poetry install --no-root --no-interaction --no-ansi

COPY entrypoint.sh .
RUN sed -i 's/\r$//g' entrypoint.sh
RUN chmod +x entrypoint.sh

ENTRYPOINT ["/backend_app/entrypoint.sh"]
