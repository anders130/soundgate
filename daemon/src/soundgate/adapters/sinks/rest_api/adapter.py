import uvicorn

from ....application.ports.outbound import SourceControlPort
from ....application.use_cases.process_event import ProcessEventUseCase
from ....application.use_cases.query_state import QueryStateUseCase
from .app import build_app


class RestApiAdapter:
    def __init__(
        self,
        query: QueryStateUseCase,
        process: ProcessEventUseCase,
        control_map: dict[str, SourceControlPort],
        port: int = 7676,
    ) -> None:
        self._app = build_app(query, process, control_map)
        self._port = port

    async def run(self) -> None:
        config = uvicorn.Config(
            self._app,
            host="0.0.0.0",
            port=self._port,
            log_level="warning",
            loop="asyncio",
        )
        await uvicorn.Server(config).serve()
