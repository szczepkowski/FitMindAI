from fastapi import FastAPI

from app.kcal_calculator import calculate

app = FastAPI()

@app.post("/chat/message")
def predict(data: dict):
    text = data["chatMessage"]
    return calculate(text)