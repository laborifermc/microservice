from fastapi import FastAPI
from infrastructure.rest.routers import router

app = FastAPI(title="API Gateway")

# On inclut les routes
app.include_router(router)

@app.get("/")
def root():
    return {"message": "Gateway is running"}

