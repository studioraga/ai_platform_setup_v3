from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Principal Platform Practice", version="0.1.0")


class DoubleRequest(BaseModel):
    value: int = Field(ge=0, le=1000)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/double")
def double(payload: DoubleRequest) -> dict[str, int]:
    return {"result": payload.value * 2}
