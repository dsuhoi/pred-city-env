# Прогнозирование негативных аспектов развития городской среды

pred-city-env - приложение на python, позволяющее построить индекс благополучности района на основе открытых данных из [open-street-map](https://www.openstreetmap.org/)

## Установка

Используете пакетный менеджер [poetry](https://python-poetry.org/) для установки зависимостей

```bash
poetry install
```

## использование

```bash
poetry run python main.py --cities "Оренбург" \
 --file_geojson "data/geo.json" \
 --file_simple_md_result "data/districts_indexed.md"
```
где:
 - `cities` - разделенный пробелами список городов, для районов которых нужно найти индекс, например, `"Оренбург"` или `"Оренбург Санкт-Петербург Волгоград"`
 - `file_geojson` - имя файла в формате `geojson`, куда будет записан конечный результат
 - `file_simple_md_result` - имя файла, куда будет записана таблица с индексами


### Пример:
```
|    | city            | district                |   beers_per_square_km |   shop_numbers |   green_area |   station_numbers |   avg_altitude_apartments |   garage_area |   retail_area |   index_level |
|---:|:----------------|:------------------------|----------------------:|---------------:|-------------:|------------------:|--------------------------:|--------------:|--------------:|--------------:|
|  0 | Волгоград       | Ворошиловский район     |            0.503489   |      0.5       |   0.615151   |          0.168831 |                 1         |    0.526473   |     0.483247  |       2.77077 |
|  1 | Волгоград       | Дзержинский район       |            0.451832   |      0.5       |   0.884272   |          0.948052 |                 0.397892  |    0.985043   |     1         |       3.49756 |
|  2 | Волгоград       | Кировский район         |            0          |      1         |   0.670155   |          0.883117 |                 0.22018   |    0.00392759 |     0         |       5.32916 |
|  3 | Волгоград       | Красноармейский район   |            0.0273987  |      1         |   0.249865   |          0        |                 0         |    0.324447   |     0.155269  |       3.74275 |
|  4 | Волгоград       | Краснооктябрьский район |            0.276477   |      1         |   0.00606549 |          0.168831 |                 0.375339  |    1          |     0.695734  |       1.82735 |
|  5 | Волгоград       | Советский район         |            0.0361252  |      0.5       |   0          |          1        |                 0.295027  |    0          |     0.294634  |       4.87421 |
|  6 | Волгоград       | Тракторозаводский район |            0.15066    |      0         |   0.0621692  |          0.012987 |                 0.390812  |    0.547136   |     0.223638  |       3.76291 |
|  7 | Волгоград       | Центральный район       |            1          |      0         |   1          |          0.285714 |                 0.397892  |    0.381714   |     0.157953  |       4.34816 |
|  8 | Оренбург        | Дзержинский район       |            0.00307996 |      0.647059  |   0          |          1        |                 0.91701   |    0.154131   |     0.0103059 |       4.26841 |
|  9 | Оренбург        | Ленинский район         |            0.028162   |      1         |   0.0585281  |          0.641509 |                 1         |    0          |     0         |       3.67188 |
| 10 | Оренбург        | Промышленный район      |            0          |      0         |   1          |          0        |                 0.0600568 |    0.0672829  |     0.152521  |       5.72014 |
| 11 | Оренбург        | Центральный район       |            1          |      0.176471  |   0.289807   |          0.716981 |                 0         |    1          |     1         |       2.83032 |
| 12 | Санкт-Петербург | Адмиралтейский район    |            0.702472   |      0.313725  |   0.0194917  |          0.221978 |                 0.122157  |    0.0175933  |     0.253554  |       3.83197 |
| 13 | Санкт-Петербург | Василеостровский район  |            0.341179   |      0.490196  |   0          |          0.323077 |                 0.459794  |    0.130924   |     0.152849  |       3.74813 |
| 14 | Санкт-Петербург | Выборгский район        |            0.124792   |      0.666667  |   0.393703   |          0.995604 |                 0.397892  |    0.139704   |     0.321942  |       4.73831 |
| 15 | Санкт-Петербург | Калининский район       |            0.209295   |      0.627451  |   0.172389   |          0.751648 |                 0.651033  |    0.699037   |     1         |       2.73722 |
| 16 | Санкт-Петербург | Кировский район         |            0.1148     |      0.431373  |   0.0381594  |          0.487912 |                 0.397892  |    0.441874   |     0.329176  |       3.81096 |
| 17 | Санкт-Петербург | Колпинский район        |            0.00946592 |      0.254902  |   0.257702   |          0.448352 |                 0.255839  |    0.125772   |     0.0496624 |       5.01041 |
| 18 | Санкт-Петербург | Красногвардейский район |            0.140099   |      0.686275  |   0.111347   |          0.672527 |                 0.627864  |    0.51726    |     0.489137  |       3.32324 |
| 19 | Санкт-Петербург | Красносельский район    |            0.0723281  |      0.588235  |   0.29508    |          0.72967  |                 0.614998  |    0.428121   |     0.322119  |       3.99895 |
| 20 | Санкт-Петербург | Кронштадтский район     |            0.0476157  |      0         |   0.307133   |          0        |                 0         |    0.223875   |     0.203245  |       4.8324  |
| 21 | Санкт-Петербург | Курортный район         |            0          |      0.156863  |   1          |          0.551648 |                 0.143033  |    0.00642889 |     0         |       6.24532 |
| 22 | Санкт-Петербург | Московский район        |            0.15655    |      0.745098  |   0.33581    |          0.646154 |                 0.511792  |    0.33714    |     0.756681  |       3.4747  |
| 23 | Санкт-Петербург | Невский район           |            0.149056   |      1         |   0.0511555  |          0.672527 |                 0.67087   |    0.565426   |     0.480994  |       2.85734 |
| 24 | Санкт-Петербург | Петроградский район     |            0.372214   |      0.0196078 |   0.274053   |          0.197802 |                 0.16093   |    0.0311919  |     0.0860067 |       4.80191 |
| 25 | Санкт-Петербург | Петродворцовый район    |            0.0084222  |      0.294118  |   0.850261   |          0.575824 |                 0.0660728 |    0.130308   |     0.0396989 |       5.88747 |
| 26 | Санкт-Петербург | Приморский район        |            0.137229   |      0.823529  |   0.522389   |          1        |                 1         |    0.202328   |     0.582194  |       3.77711 |
| 27 | Санкт-Петербург | Пушкинский район        |            0.0111777  |      0.372549  |   0.339049   |          0.694505 |                 0.145023  |    0.040699   |     0.102463  |       5.36164 |
| 28 | Санкт-Петербург | Фрунзенский район       |            0.172502   |      0.745098  |   0.152554   |          0.549451 |                 0.583681  |    1          |     0.980283  |       2.22044 |
| 29 | Санкт-Петербург | Tsentralny District     |            1          |      0.254902  |   0.028719   |          0.323077 |                 0.0736781 |    0          |     0.388661  |       3.63455 |
```

## Contributing

Запросы на извлечение приветствуются. Что касается серьезных изменений, пожалуйста, сначала откройте проблему
, чтобы обсудить, что вы хотели бы изменить.

Пожалуйста, не забудьте соответствующим образом обновить тесты.
## License

[MIT](https://choosealicense.com/licenses/mit/)