import pytest


async def test_list_cities(ac, create_data):
    responce = await ac.get("geo/cities")
    assert responce.status_code == 200
    assert len(responce.json()) == 2


# async def test_get_city(ac, create_data):
#     pass
