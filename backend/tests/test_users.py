import pytest


async def test_login_user(ac, create_data):
    response = await ac.post(
        "users/login", data={"username": "admin", "password": "pass"}
    )
    assert response.status_code == 200
    assert response.json()["access_token"] != ""


async def test_get_users(ac, create_data):
    response = await ac.get("users/")
    assert response.status_code == 200
    assert len(response.json()["users"]) == 4


@pytest.mark.parametrize("username", ["user2", "admin"])
async def test_find_user(username, ac, create_data):
    response = await ac.get(f"users/{username}")
    assert response.status_code == 200
    assert response.json()["username"] == username
