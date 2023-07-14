import folium
import pandas as pd
import streamlit as st
from streamlit_folium import folium_static

st.set_page_config(layout="wide")
st.header("Карта геттоизации районов Санкт-Петербурга")
json1 = f"frontend/MVP/saint_pet.geojson"

population = pd.read_csv("frontend/MVP/saint_pet_population.csv")


m = folium.Map(
    location=[59.95, 30.19],
    tiles="CartoDB positron",
    name="Light Map",
    zoom_start=10,
    # attr="My Data Attribution",
)

choice_selected = st.selectbox(
    "Выбор деления карты ", ["Деление на районы", "Деление на кварталы"]
)
choice_metric = st.selectbox("Выбор метрики ", ["Население", "Площадь"])
folium.Choropleth(
    geo_data=json1,
    name="choropleth",
    data=population,
    columns=["район", choice_metric.lower()],
    # columns=["Районы/кварталы", choice_selected],
    key_on="feature.properties.district",
    fill_color="YlOrRd",
    fill_opacity=0.8,
    line_opacity=0.1,
    legend_name=choice_metric,
).add_to(m)
folium.features.GeoJson(
    json1,
    name="Название субъекта",
    popup=folium.features.GeoJsonPopup(fields=["district"]),
).add_to(m)
folium_static(m, width=1600, height=950)
