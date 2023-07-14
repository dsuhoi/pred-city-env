import folium
import pandas as pd
import streamlit as st
from streamlit_folium import folium_static

BASE_DIR = "frontend/MVP/"

st.set_page_config(layout="wide")
st.header("Карта геттоизации районов Санкт-Петербурга")


json1 = BASE_DIR + "saint_pet.geojson"

saint_data = pd.read_csv(BASE_DIR + "saint_pet_data.csv")


m = folium.Map(
    location=[59.95, 30.19],
    tiles="CartoDB positron",
    name="Light Map",
    zoom_start=10,
)

choice_selected = st.selectbox(
    "Выбор деления карты ", ["Деление на районы", "Деление на кварталы"]
)
choice_metric = st.selectbox(
    "Выбор метрики ", ["Население", "Площадь", "Индекс счастья"]
)
folium.Choropleth(
    geo_data=json1,
    name="choropleth",
    data=saint_data,
    columns=["район", choice_metric.lower()],
    key_on="feature.properties.district",
    fill_color="YlOrRd",
    fill_opacity=0.5,
    line_opacity=0.1,
    legend_name=choice_metric,
).add_to(m)
folium.features.GeoJson(
    json1,
    name="Название субъекта",
    popup=folium.features.GeoJsonPopup(fields=["district", "population", "area"]),
).add_to(m)
folium_static(m, width=1600, height=950)
