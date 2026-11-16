"""R03 research fixture: deliberately isolated from production platform_demo.py.

v1 is the current /v1/double contract, reproduced without modifying it.
v2 compatible adds an optional memo; v2 breaking narrows range and requires memo.
No auth, rate limiting or production readiness is claimed.
"""
from fastapi import FastAPI
from pydantic import BaseModel, Field

class DoubleResponse(BaseModel):
    result: int

class V1DoubleRequest(BaseModel):
    value: int = Field(ge=0, le=1000)

class V2CompatibleRequest(BaseModel):
    value: int = Field(ge=0, le=1000)
    memo: str | None = None

class V2BreakingRequest(BaseModel):
    value: int = Field(ge=0, le=100)
    memo: str


def make_app(version: str) -> FastAPI:
    if version not in {'v1', 'v2-compatible', 'v2-breaking'}:
        raise ValueError(f'unsupported fixture version {version!r}')
    app = FastAPI(title='R03 Isolated Compatibility Research', version=version)

    @app.get('/health')
    def health() -> dict[str, str]:
        return {'status': 'ok'}

    if version == 'v1':
        @app.post('/v1/double', response_model=DoubleResponse)
        def double_v1(payload: V1DoubleRequest) -> dict[str, int]:
            return {'result': payload.value * 2}
    elif version == 'v2-compatible':
        @app.post('/v1/double', response_model=DoubleResponse)
        def double_v2_compatible(payload: V2CompatibleRequest) -> dict[str, int]:
            return {'result': payload.value * 2}
    else:
        @app.post('/v1/double', response_model=DoubleResponse)
        def double_v2_breaking(payload: V2BreakingRequest) -> dict[str, int]:
            return {'result': payload.value * 2}
    return app
