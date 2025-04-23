import fastapi
from app.functions import main
app = fastapi.FastAPI()

@app.get("/")
def read_root():
    return {"message": "check the docs at /docs"}
  
@app.get("/search")
def search(query: str):
    return main(query)

