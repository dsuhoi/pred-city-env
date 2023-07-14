FROM python:3.10-slim
EXPOSE 8501
WORKDIR /frontend_mvp
RUN pip3 install poetry
COPY *.py *.geojson *.csv poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false \
&& poetry install --no-interaction --no-ansi
CMD streamlit run visual.py
