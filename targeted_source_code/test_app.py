from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_create_item():
    response = client.post(
        "/items/",
        json={"name": "test_item"}
    )
    assert response.status_code == 200
    assert response.json() == {"name": "test_item", "status": "created"}
