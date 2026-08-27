from enum import Enum


class GetHealthResponse200Status(str, Enum):
    DEGRADED = "degraded"
    ERROR = "error"
    OK = "ok"

    def __str__(self) -> str:
        return str(self.value)
