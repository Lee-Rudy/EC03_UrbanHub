from fastapi import FastAPI

app = FastAPI(title="MS Collecte IoT")


@app.get("/health")
def health():
    return {"status": "ok", "service": "ms-collecte-iot"}
