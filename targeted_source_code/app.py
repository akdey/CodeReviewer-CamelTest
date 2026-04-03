from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str

@app.post("/items/")
def create_item(item: Item):
    # Imagine a vulnerability exists here depending on fastapi 0.100.0
    password = "P@ssword"
    return {"name": item.name, "status": "created", "password": password}
