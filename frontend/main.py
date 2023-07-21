import folium
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import folium_static

URL = "http://backend:8000/geo"

all_cities = requests.get(f"{URL}/cities").json()
select_city_vars = {"Все города": "all"} | {
    city["title"]: city["id"] for city in all_cities
}
select_metrics_vars = {
    "Общая площадь": "common_area",
    "Количество пивных магазинов на км^2": "beers_per_square_km",
    "Количество магазинов": "shop_numbers",
    "Площадь озелененной территории": "green_area",
    "Количество остановок": "station_numbers",
    "Высотность зданий": "avg_altitude_apartments",
    "Площадь гаражных территорий": "garage_area",
    "Площадь рынков и овощебаз": "retail_area",
}

st.set_page_config(page_title="Карта метрик городов", layout="wide")
st.header("Карта метрик городов РФ")
choice_city = st.selectbox("Выбор города ", list(select_city_vars.keys()))
current_city = select_city_vars[choice_city]
choice_metric = st.selectbox(
    "Выбор метрики ",
    list(select_metrics_vars.keys()),
    disabled=current_city == "all",
)
current_metric = select_metrics_vars[choice_metric]


def read_df_from_geojson(gj: dict) -> pd.DataFrame:
    data = {"title": []} | {key: [] for key in select_metrics_vars.values()}
    for dist in gj["features"]:
        dist = dist["properties"]
        for key in dist:
            data[key].append(dist[key])
    return pd.DataFrame.from_dict(data)


if current_city == "all":
    m = folium.Map(
        location=[56.535257, 64.028321],
        tiles="CartoDB positron",
        name="Light Map",
        zoom_start=5,
    )
    geojson = requests.get(f"{URL}/cities", params={"geojson": True}).json()
    folium.Choropleth(geo_data=geojson).add_to(m)
    folium.features.GeoJson(
        geojson, name="Свойства", popup=folium.features.GeoJsonPopup(fields=["title"])
    ).add_to(m)
else:
    geojson = requests.get(
        f"{URL}/districts", params={"city_id": current_city, "geojson": True}
    ).json()
    df_data = read_df_from_geojson(geojson)

    m = folium.Map(
        location=geojson["features"][0]["geometry"]["coordinates"][0][0][0][::-1],
        tiles="CartoDB positron",
        name="Light Map",
        zoom_start=10,
    )
    folium.Choropleth(
        geo_data=geojson,
        name="choropleth",
        data=df_data,
        columns=["title", current_metric],
        key_on="feature.properties.title",
        fill_color="YlOrRd",
        fill_opacity=0.5,
        line_opacity=0.1,
        legend_name=choice_metric,
    ).add_to(m)
    folium.features.GeoJson(
        geojson,
        name="Свойства",
        popup=folium.features.GeoJsonPopup(
            fields=["title"] + list(select_metrics_vars.values())
        ),
    ).add_to(m)
folium_static(m, width=1600, height=950)
