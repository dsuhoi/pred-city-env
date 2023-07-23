import logging

import numpy as np
import pandas as pd
from pandas import DataFrame

import osmnx as ox
from collect_metric import collect_metrics, measurable_metrics
import traceback
import orjson
from collections import defaultdict
from shapely import Polygon, MultiPolygon

import click

def fetch_raw_metrics(
        target_cities: set[str],
        districts_list_filepath:str=None):
    if districts_list_filepath is None:
        districts_list_filepath = 'data/districts.json'
    raw_metrics = {}
    with open('data/districts.json', 'rb') as file:
        cities = orjson.loads(file.read())
    for [city_name, district_list] in cities.items():
        if city_name not in target_cities:
            continue
        logging.info(f"Start collection from city: {city_name}")
        for district_name in district_list:
            try:
                logging.info(f"Start collection from district: {district_name}")
                district_gdf = ox.geocode_to_gdf(f'{city_name}, {district_name}', which_result=1)
                district_metrics = collect_metrics(district_gdf, measurable_metrics)
                if raw_metrics.get(city_name) is None:
                    raw_metrics[city_name] = {
                        'districts': {}
                    }
                raw_metrics[city_name]['districts'][district_name] = district_metrics
            except Exception as exc:
                # traceback.print_tb(exc.__traceback__)
                logging.error(f'Something went wrong with {city_name} {district_name}')
    return raw_metrics


def calculate_index(raw_metrics=None):
    if raw_metrics is None:
        try:
            with open('data/metrics_outputs.json', 'r') as result_file:
                districts_data = orjson.loads(result_file.read())
        except FileNotFoundError as exc:
            logging.error(f'file {"data/metrics_outputs.json"} doesn\'t exist!')
            raise exc
    else:
        districts_data = raw_metrics

    data_dict = defaultdict(list)
    for city_name, city in districts_data.items():
        for district_name, district in city['districts'].items():
            data_dict['city'].append(city_name)
            data_dict['district'].append(district_name)
            for metric_name, metric in district['features'][0]['properties'].items():
                if metric_name == 'name':
                    continue
                data_dict[metric_name].append(metric)
    df = pd.DataFrame(data_dict)
    metrics_processes = {
        'beers_per_square_km': lambda x: 1 - x,
        'shop_numbers': lambda x: 1 - x,
        'green_area': lambda x: x,
        'station_numbers': lambda x: x,
        'avg_altitude_apartments': lambda x: 1 - x,
        'garage_area': lambda x: 1 - x,
        'retail_area': lambda x: 1 - x
    }

    normalized_df = df[['city', 'district']]
    for metric_index, metric_name in enumerate(metrics_processes.keys()):
        normalized_metric_value = []
        for city_name in normalized_df['city'].unique():
            df_by_city = df[df['city'] == city_name]
            metric_col = df_by_city[metric_name]
            normalized_metric_value.extend(
                list((metric_col - metric_col.min()) / (metric_col.max() - metric_col.min())))
        normalized_df.insert(2 + metric_index, f'{metric_name}', normalized_metric_value)
    processed_df = df[['city', 'district']]
    for metric_index, metric_name in enumerate(metrics_processes.keys()):
        mean = normalized_df[metric_name].mean()
        notnull_column = normalized_df[metric_name].replace(np.nan, mean)
        processed_df.insert(len(processed_df.columns), metric_name, notnull_column)
    levels = [sum(
        metric_fun(float(row[metric_name]))
        for metric_name, metric_fun in metrics_processes.items())
        for row_index, row in processed_df.iterrows()
    ]
    processed_df.insert(len(processed_df.columns), 'index_level', levels)
    return processed_df


def form_geo_json(indexed_districts: DataFrame, metrics_outputs:dict,
                  districts_geojson_filepath='data/districts_indexed.json'):
    geo_json = {
        'type': "FeatureCollection",
        'features': []
    }

    metrics_processes = {
        'beers_per_square_km',
        'shop_numbers',
        'green_area',
        'station_numbers',
        'avg_altitude_apartments',
        'garage_area',
        'retail_area',
    }
    for city_index, (city_name, city) in enumerate(metrics_outputs.items()):
        city_gdf = ox.geocode_to_gdf(f'{city_name}', which_result=1)
        city_geom, *_ = city_gdf.geometry
        if isinstance(city_geom, Polygon):
            city_geom = MultiPolygon([city_geom])
        city_gdf.geometry[0] = city_geom

        geo_json['features'].append(
            {
                "type": "Feature",
                "properties": {
                    "title": city_name
                },
                "geometry": orjson.loads(city_gdf.to_json())['features'][0]['geometry'],
                "districts": {
                    "type": "FeatureCollection",
                    "features": []
                },
            },
        )
        for district_index, (district_name, district) in enumerate(city['districts'].items()):
            try:
                district_feature, *_ = district['features']
                district_feature.pop('id')

                indexed_json = orjson.loads(
                    indexed_districts[(indexed_districts['city'] == city_name)
                                      & (indexed_districts['district'] == district_name)].to_json())
                processed_indexed_json = {}
                for key, val in indexed_json.items():
                    processed_indexed_json[key] = val[list(val.keys())[0]]
                for prop in metrics_processes:
                    district_feature['properties'][f'{prop}_normalized'] = processed_indexed_json[prop]
                district_feature['properties']['index_level'] = processed_indexed_json['index_level']
                district_feature['properties']['title'] = processed_indexed_json['district']
                geo_json['features'][-1]['districts']['features'].append(district_feature)

            except Exception as exc:
                traceback.print_tb(exc.__traceback__)
    with open(districts_geojson_filepath, 'wb') as file:
        file.write(orjson.dumps(geo_json))

    return geo_json

@click.command()
@click.option("--cities", default=['Томск', 'Новосибирск', 'Санкт-Петербург'], help="Enter list of cities between spaces")
@click.option("--file_geojson", default='data/districts_indexed.json', help="Enter the file with results of calculated index for districts in json")
@click.option("--file_simple_md_result", default='data/districts_indexed.md', help="Enter the file with results")
def calc_index(cities: str,file_geojson: str, file_simple_md_result:str):
    cities_set = set(cities.split(' '))
    districts_raw_metrics = fetch_raw_metrics(target_cities=cities_set)
    indexed_districts = calculate_index(districts_raw_metrics)
    with open(file_simple_md_result,'w') as file:
        file.write(indexed_districts.to_markdown())
    form_geo_json(indexed_districts,districts_raw_metrics,file_geojson)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    calc_index()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
