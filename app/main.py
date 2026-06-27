from fastapi import FastAPI

from app.api.routes import router


app = FastAPI(
    title="Legal Doc AI Pipeline",
    version="0.1.0",
    description="Local-first legal document intelligence pipeline.",
)

app.include_router(router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
