from fastapi import FastAPI

app = FastAPI(title="User Management Microservice")

@app.get("/health")
def health():
    return {"status": "ok", "service": "ms-user"}