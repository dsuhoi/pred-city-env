import pytest


async def test_list_car(ac, create_data):
    response = await ac.get("cars/")
    assert response.status_code == 200
    assert response.json()[0]["id"] == 1


async def test_post_car(ac, create_data):
    response = await ac.post("cars/", params={"start_location": 34470})
    assert response.status_code == 200
    assert len(response.json()["car_number"]) == 5


@pytest.mark.parametrize("data,result", [({"current_loc": 15951}, {"code": 200})])
async def test_update_car(data, result, ac, create_data):
    response = await ac.patch("cars/", params={"car_id": 1}, json=data)
    assert response.status_code == result["code"]
    assert response.json()["current_loc"] == data["current_loc"]
