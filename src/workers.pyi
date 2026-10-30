from typing import Any, Mapping

class Response:
    def __init__(
        self,
        body: str | None = ...,
        *,
        status: int = ...,
        headers: Mapping[str, str] | None = ...,
    ) -> None: ...

class WorkerEntrypoint:
    env: Any
