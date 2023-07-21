# import json
# import pathlib
import random

import folium
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import folium_static

# BASE_DIR = pathlib.Path(__file__).parent.resolve().joinpath("data")
# geojson_path = BASE_DIR.joinpath("saint_pet.geojson")


def read_df_from_geojson(gj: dict) -> pd.DataFrame:
    data = {"район": [], "население": [], "площадь": [], "индекс счастья": []}
    for dist in gj["features"]:
        dist = dist["properties"]
        data["район"].append(dist["title"])
        data["население"].append(dist["population"])
        data["площадь"].append(dist["area"])
        data["индекс счастья"].append(random.randint(1, 20))
    return pd.DataFrame.from_dict(data)


# with open(geojson_path, "r") as f:
#     geojson = json.load(f)
spb_id = requests.get(
    "http://0.0.0.0:8000/geo/cities", params={"title": "Санкт-Петербург"}
).json()["id"]
geojson = requests.get(
    "http://0.0.0.0:8000/geo/districts", params={"city_id": spb_id, "geojson": True}
).json()
saint_data = read_df_from_geojson(geojson)

m = folium.Map(
    location=[59.95, 30.19],
    tiles="CartoDB positron",
    name="Light Map",
    zoom_start=10,
)

st.set_page_config(layout="wide")
st.header("Карта геттоизации районов Санкт-Петербурга")

choice_selected = st.selectbox(
    "Выбор деления карты ", ["Деление на районы", "Деление на кварталы"]
)
choice_metric = st.selectbox(
    "Выбор метрики ", ["Население", "Площадь", "Индекс счастья"]
)
folium.Choropleth(
    geo_data=geojson,
    name="choropleth",
    data=saint_data,
    columns=["район", choice_metric.lower()],
    key_on="feature.properties.title",
    fill_color="YlOrRd",
    fill_opacity=0.5,
    line_opacity=0.1,
    legend_name=choice_metric,
).add_to(m)
folium.features.GeoJson(
    geojson,
    name="Название субъекта",
    popup=folium.features.GeoJsonPopup(fields=["title", "population", "area"]),
).add_to(m)
folium_static(m, width=1600, height=950)
