FROM python:3.10-slim

WORKDIR /frontend_app
RUN pip3 install poetry

COPY *.py *.geojson poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false \
&& poetry install --no-root --no-interaction --no-ansi

CMD ["streamlit", "run", "main.py"]
#, "--server.address=0.0.0.0"]
