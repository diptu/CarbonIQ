# ima_service/app/main.py
from fastapi import FastAPI
from ima_service.app.api.v1.api import api_router as api_v1_router
from ima_service.app.api.v2.api import api_router as api_v2_router

app = FastAPI(title="IMA Service API")


@app.get("/")
def read_root():
    return {"message": "IMA Service is alive!"}


# Mount versioned APIs
app.include_router(api_v1_router, prefix="/api/v1")
# app.include_router(api_v2_router, prefix="/api/v2")
