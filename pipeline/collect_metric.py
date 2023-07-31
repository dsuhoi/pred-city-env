import logging  # Импорт модуля для логирования
from collections import defaultdict  # Импорт функции defaultdict из модуля collections
from typing import Literal, Any  # Импорт типов Literal и Any из модуля typing

import orjson.orjson
import osmnx as ox  # Импорт библиотеки osmnx с псевдонимом ox
import pandas as pd
from geopandas import GeoDataFrame, overlay  # Импорт класса GeoDataFrame и функции overlay из модуля geopandas
from shapely import Polygon, MultiPolygon  # Импорт класса Polygon и функции union_all из модуля shapely

MetricLiterals = Literal[
    'beers_per_square_km', 'shop_numbers', 'green_area', 'station_numbers', 'avg_altitude_apartments', 'garage_area', 'retail_area']


class MetricCollector:
    """
    Класс MetricCollector содержит методы для сбора различных метрик в заданных географических районах.
    """

    @classmethod
    def _pub_numbers(cls, district: Polygon, common_area: float) -> float:
        """
        Метод собирает метрику, связанную с количеством пабов в заданном районе (district).
        :param district: Полигон, представляющий географический район.
        :param common_area: Площадь общего района, на которую приходится этот полигон.
        :return: Значение собранной метрики (число пабов на площадь в квадратных километрах).
        """

        """
        - 'amenity': 'pub':
        - 'shop': ['brewing_supplies', 'alcohol']
        :param district:
        :return:
        """
        beers = ox.features_from_polygon(district, tags={
            'shop': ['brewing_supplies', 'alcohol'],
            'amenity': ['pub']
        })
        # logging.debug(f"{beers}")
        return len(beers) / (common_area / 1e6)

    @classmethod
    def _shop_numbers(cls, district: Polygon) -> int:
        """
        - 'amenity': 'pub':
        - 'shop': ['brewing_supplies', 'alcohol']
        :param district:
        :return:
        """
        shops = ox.features_from_polygon(district, tags={
            'name': ['Пятёрочка']
        })
        # Спар, SPAR, Spar, Spar Express, SPAR Express, Spar express, Спар экспресс, Евроспар, ЕВРОСПАР, EUROSPAR,
        # Eurospar, EuroSPAR, Eurospar Express. EuroSPAR Express, Eurospar express, Interspar, Интерспар Пятёрочка (
        # е/ё); иногда дублируется ритейл и магаз logging.debug(f"{beers}")

        return len(shops)

    @classmethod
    def _green_area(cls, district: GeoDataFrame, common_area: float) -> float:
        """
        Метод собирает метрику, связанную с зелеными зонами в заданном районе (district).
        :param district: GeoDataFrame, представляющий географический район.
        :param common_area: Площадь общего района, на которую приходится этот район.
        :return: Значение доли зеленых зон на общей площади района.
        """
        greens: GeoDataFrame = ox.features_from_polygon(district['geometry'].all(), tags={
            'leisure': ['park', 'garden', 'nature_reserve'],
            'landuse': ['grass', 'forest', 'recreation_ground'],
            'natural': ['wood', 'grassland', 'tree', 'tree_row', 'scrub', 'wood']
        })
        clipped_greens = overlay(greens[greens.geometry.geom_type.isin(['Polygon', 'MultiPolygon'])],
                                 district, how='intersection', keep_geom_type=True)
        # print(clipped_greens)
        # united_clipped_greens = union_all(clipped_greens['geometry']).area
        # green_area = united_clipped_greens.area
        green_area = clipped_greens.to_crs(epsg=6933).area.sum()
        logging.debug(f'green area = {green_area}')
        logging.debug(f'common area = {common_area}')

        return green_area / common_area

    @classmethod
    def _station_numbers(cls, district: Polygon) -> int:
        """
        - 'amenity': 'pub':
        - 'shop': ['brewing_supplies', 'alcohol']
        :param district:
        :return:
        """
        stations = ox.features_from_polygon(district, tags={
            'highway': ['bus_stop']
        })
        # Спар, SPAR, Spar, Spar Express, SPAR Express, Spar express, Спар экспресс, Евроспар, ЕВРОСПАР, EUROSPAR, Eurospar, EuroSPAR, Eurospar Express. EuroSPAR Express, Eurospar express, Interspar, Интерспар
        # Пятёрочка (е/ё); иногда дублируется ритейл и магаз
        # logging.debug(f"{beers}")

        return len(stations)

    @classmethod
    def _avg_altitude_apartments(cls, district: Polygon) -> float:
        """
        Метод собирает метрику, связанную со средней высотой зданий типа "апартаменты" в заданном районе (district).
        :param district: Полигон, представляющий географический район.
        :return: Значение средней высоты апартаментов.
        """
        apartments: GeoDataFrame = ox.features_from_polygon(district, tags={
            'building': ['apartments', 'residential'],  # 'residential' is discussing
        })
        apartments_with_defined_floors = apartments[apartments['building:levels'].notnull()]

        return pd.to_numeric(apartments_with_defined_floors['building:levels'],downcast='float').sum() / len(
            apartments_with_defined_floors)

    @classmethod
    def _garage_area(cls, district: GeoDataFrame, common_area: float) -> float:
        """
        Метод собирает метрику, связанную с площадью гаражей в заданном районе (district).
        :param district: GeoDataFrame, представляющий географический район.
        :param common_area: Площадь общего района, на которую приходится этот район.
        :return: Значение доли площади гаражей на общей площади района.
        """
        garages: GeoDataFrame = ox.features_from_polygon(district['geometry'].all(), tags={
            'building': ['garages', 'garage'],
            'landuse': ['garages'],
        })
        clipped_garages = overlay(garages[garages.geometry.geom_type.isin(['Polygon', 'MultiPolygon'])],
                                  district, how='intersection', keep_geom_type=True)
        garage_area = clipped_garages.to_crs(epsg=6933).area.sum()
        logging.debug(f'garage area = {garage_area}')
        logging.debug(f'common area = {common_area}')

        return garage_area / common_area

    @classmethod
    def _retail_area(cls, district: GeoDataFrame, common_area: float) -> float:
        """
        Метод собирает метрику, связанную с площадью оптовых рынков в заданном районе (district).
        :param district: GeoDataFrame, представляющий географический район.
        :param common_area: Площадь общего района, на которую приходится этот район.
        :return: Значение доли площади оптовых рынков на общей площади района.
        """
        retails: GeoDataFrame = ox.features_from_polygon(district['geometry'].all(), tags={
            'landuse': ['retail'], 'amenity': ['marketplace']
        })
        clipped_retails = overlay(retails[retails.geometry.geom_type.isin(['Polygon', 'MultiPolygon'])],
                                  district, how='intersection', keep_geom_type=True)
        retail_area = clipped_retails.to_crs(epsg=6933).area.sum()
        logging.debug(f'retail area = {retail_area}')
        logging.debug(f'common area = {common_area}')

        return retail_area / common_area

    @classmethod
    def fetch_metrics(cls, districts: GeoDataFrame, metrics) -> dict[
        MetricLiterals, Any]:
        """
        Приватный статический метод для сбора метрик для всех переданных географических районов.
        :param districts: GeoDataFrame с информацией о географических районах.
        :param metrics: Переменное число аргументов для указания, какие метрики собирать.
        :return: Словарь с результатами собранных метрик.
        """
        data = defaultdict(list)
        crs = districts.to_crs({'proj': 'cea'})

        for index, district in districts.iterrows():
            data['title'].append(district['display_name'])
            common_area = crs.iloc[[index]]['geometry'].area.sum()
            # print(f'{}')
            data['common_area'].append(common_area / 1e6)
            for metric_name, is_metric_collected in metrics.items():
                if not is_metric_collected:
                    continue
                try:
                    match metric_name:
                        case 'beers_per_square_km':
                            data[metric_name].append(cls._pub_numbers(district['geometry'], common_area))
                        case 'shop_numbers':
                            data[metric_name].append(cls._shop_numbers(district['geometry']))
                        case 'green_area':
                            data[metric_name].append(cls._green_area(districts.iloc[[index]], common_area))
                        case 'station_numbers':
                            data[metric_name].append(cls._station_numbers(district['geometry']))
                        case 'avg_altitude_apartments':
                            data[metric_name].append(cls._avg_altitude_apartments(district['geometry']))
                        case 'garage_area':
                            data[metric_name].append(cls._garage_area(districts.iloc[[index]], common_area))
                        case 'retail_area':
                            data[metric_name].append(cls._retail_area(districts.iloc[[index]], common_area))

                except Exception as exc:
                    logging.warning(f'Something went wrong with {metric_name} for {district["display_name"]}')
                    print(f'{exc.args}')
                    data[metric_name].append(None)

        return data


logging.getLogger().setLevel(logging.INFO)
logging.getLogger("urllib3").setLevel(logging.INFO)

measurable_metrics = {
        'beers_per_square_km': True,
        'shop_numbers': True,
        'green_area': True,
        'station_numbers': True,
        'avg_altitude_apartments': True,
        'garage_area': True,
        'retail_area': True
    }

def collect_metrics(districts: GeoDataFrame, metrics: dict[str,bool] = None):
    """
    Функция для сбора метрик для заданных географических районов по их именам.
    :param districts:
    :param metrics: Переменное число аргументов для указания, какие метрики собирать.
    :return: DataFrame с результатами собранных метрик.
    """

    if metrics is None:
        metrics = measurable_metrics
    metrics_for_districts = MetricCollector.fetch_metrics(districts, metrics)
    geos = []
    for geo in districts.geometry.to_list():
        if isinstance(geo, MultiPolygon):
            geos.append(geo)
        if isinstance(geo, Polygon):
            geos.append(MultiPolygon([geo]))

    metrics_for_districts['geometry'] = geos
    # print(metrics_for_districts)
    return orjson.loads(GeoDataFrame(metrics_for_districts).to_json())
    # return DataFrame(metrics_for_districts)
