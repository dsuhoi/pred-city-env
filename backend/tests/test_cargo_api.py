import pytest


async def test_list_cargo(ac, create_data):
    response = await ac.get("cargo/", params={"distance": 450})
    assert response.status_code == 200
    assert response.json()[0] == {
        "count_cars_nerby": 3,
        "delivery": 58045,
        "id": 1,
        "pick_up": 12933,
    }


async def test_post_cargo(ac, create_data):
    response = await ac.post(
        "cargo/",
        json={
            "pick_up": 39092,
            "delivery": 15951,
            "weight": 500,
            "description": "Text4",
        },
    )
    assert response.status_code == 200
    assert response.json()["id"]


async def test_get_cargo(ac, create_data):
    response = await ac.get("cargo/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1


@pytest.mark.parametrize("data,result", [({"weight": 100}, {"code": 200})])
async def test_update_cargo(data, result, ac, create_data):
    response = await ac.patch("cargo/", params={"cargo_id": 1}, json=data)
    assert response.status_code == result["code"]
    assert response.json()["weight"] == data["weight"]


async def test_delete_cargo(ac, create_data):
    response = await ac.delete("cargo/1")
    assert response.status_code == 200
