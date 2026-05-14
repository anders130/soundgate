from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from ....application.ports.outbound import SourceControlPort
from ....application.use_cases.process_event import ProcessEventUseCase
from ....application.use_cases.query_state import QueryStateUseCase
from ....domain.events import PlaybackState, PlayerEvent


class _VolumeReq(BaseModel):
    level: float


class _SeekReq(BaseModel):
    position_s: float


class _SourceReq(BaseModel):
    name: str


def build_app(
    query: QueryStateUseCase,
    process: ProcessEventUseCase,
    control_map: dict[str, SourceControlPort],
) -> FastAPI:
    app = FastAPI(docs_url=None, redoc_url=None)

    @app.get("/state")
    async def get_state() -> dict:
        active = query.active_source()
        sources = [
            {"name": s.name, "state": s.state} for s in query.all_sources().values()
        ]
        if active is None:
            return {
                "state": "stopped",
                "source": None,
                "title": None,
                "artist": None,
                "album": None,
                "art_url": None,
                "position_s": 0.0,
                "duration_s": None,
                "volume": process.volume,
                "sources": sources,
            }
        m = active.metadata
        return {
            "state": active.state,
            "source": active.name,
            "title": m.title,
            "artist": m.artist,
            "album": m.album,
            "art_url": m.art_url,
            "position_s": active.position_us / 1_000_000 if active.position_us else 0.0,
            "duration_s": m.duration_us / 1_000_000 if m.duration_us else None,
            "volume": process.volume,
            "sources": sources,
        }

    @app.post("/volume")
    async def set_volume(req: _VolumeReq) -> dict:
        await process.set_volume(req.level)
        return {"ok": True}

    async def _ctrl(action: str) -> dict:
        active = query.active_source()
        if active is None or active.name not in control_map:
            return {"ok": False, "reason": "no controllable active source"}
        fn = getattr(control_map[active.name], action, None)
        if fn is None:
            return {"ok": False, "reason": "no controllable active source"}
        await fn()
        return {"ok": True}

    @app.post("/play")
    async def play() -> dict:
        return await _ctrl("play")

    @app.post("/pause")
    async def pause() -> dict:
        return await _ctrl("pause")

    @app.post("/stop")
    async def stop() -> dict:
        return await _ctrl("stop")

    @app.post("/next")
    async def next_track() -> dict:
        return await _ctrl("next_track")

    @app.post("/previous")
    async def previous_track() -> dict:
        return await _ctrl("previous_track")

    @app.post("/seek")
    async def seek(req: _SeekReq) -> dict:
        active = query.active_source()
        if active is None or active.name not in control_map:
            return {"ok": False, "reason": "no controllable active source"}
        await control_map[active.name].seek(req.position_s)
        return {"ok": True}

    @app.post("/source")
    async def select_source(req: _SourceReq) -> dict:
        if req.name not in query.all_sources():
            raise HTTPException(404, f"unknown source: {req.name}")
        await process.handle_event(
            PlayerEvent(source=req.name, state=PlaybackState.PLAYING)
        )
        return {"ok": True}

    return app
