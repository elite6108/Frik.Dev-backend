from fastapi import FastAPI
from apis.ai.template import router as template_router

app = FastAPI()

app.include_router(template_router, prefix="/ai", tags=["AI"])
@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


