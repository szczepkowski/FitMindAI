from fastapi import FastAPI

from app.kcal_calculator import calculate

app = FastAPI()

@app.post("/chat/message")
def predict(data: dict):
    text = data["chatMessage"]
    return calculate(text)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)