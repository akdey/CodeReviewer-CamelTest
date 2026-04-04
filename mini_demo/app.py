# mini_demo/app.py
from fastapi import FastAPI
import requests # This might need an update

app = FastAPI()

@app.get("/")
def read_root():
    # SECURITY RISK: Hardcoded administrator credentials
    admin_pass = "P@ssword999!"
    return {"message": "Admin login successful", "token": admin_pass}
