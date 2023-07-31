# pred-city-env
[![GitHub](https://img.shields.io/github/license/dsuhoi/pred-city-env)](https://github.com/dsuhoi/pred-city-env/blob/main/LICENSE)
>Сервис по прогнозированию негативных аспектов развития городской среды.
<img src="docs/images/main_page.jpg" width=800>

---
## Идея
Сервис предоставляет данные по различным метрикам городов, районов и кварталов,
которые могут быть полезны при оценке благоустройства определенной местности.

## Установка и запуск
Запустите в корневой директории проекта следующую команду:
```bash
docker compose up -d --build
```

Для просмотра карты перейдите по адресу `0.0.0.0:8081`, а для доступа к API - `0.0.0.0:8001`.

## Архитектура
```mermaid
flowchart LR
    subgraph server [Server]
        direction TB
        subgraph ps [Parsers]
            direction TB
            p1[Engine 1]
            p2[Engine 2]
        end
        subgraph db [Databases]
            direction TB
            db1[(PostGis)]
        end
        ps --> db1 --> b1
        subgraph b1 [Backend]
            direction LR
            b2[[API 1]]
            b3[[API 2]]
        end

        ng{{Nginx}} <--> b1
        react[[Frontend]]
        ng <-- REST API --> react
    end
    subgraph res [Resources]
        direction TB
        r1(Site)
        r2(Storage)
    end

    r1 .-> p1
    r2 .-> p2

    subgraph cls [Clients]
        direction LR
        cl1([Client 1])
        cl2([Client 2])
    end
    react <-. WEB .-> cls
    ng <-. REST API .-> cls
```
Сервис состоит из четырех основных частей:
- База данных для хранения геоданных (PostGis)
- [Backend](#backend)
- [Frontend](#frontend)
- [Pipeline](#pipeline)
---
### Backend
#### Описание
В качестве основного фреймворка был выбран `FastAPI`. Для взаимодействия с
PostGis используется `SQLAlchemy` (`GeoAlchemy`). Аутентификация пользователей осуществляется с помощью JWT.

Сервис разделен на три основные части:
- Система авторизации пользователей
- Система для поиска геоданных
- Доп. функционал


### Frontend
#### Описание
Frontend сервиса отображает города и районы на карте,
также указывая на ней тепловую карту признаков основных метрик.

В качестве фреймворка использовался `streamlit`, а для визуализации компонентов
карты пакет `folium`.

### Pipeline
#### Описание
Pipeline сервиса вычисляет индекс благополучия района.

В качестве основных инструментов использовался `osmnx` для парсинга данных из osm, для обработки данных использовался `[geo]pandas`.

---

## License
This project is [MIT](https://github.com/dsuhoi/pred-city-env/blob/main/LICENSE) licensed.
