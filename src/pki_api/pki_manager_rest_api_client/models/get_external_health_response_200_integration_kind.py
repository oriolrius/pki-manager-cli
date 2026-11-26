from enum import Enum


class GetExternalHealthResponse200IntegrationKind(str, Enum):
    GENERIC = "generic"
    KUBERNETES = "kubernetes"
    SCEP = "scep"

    def __str__(self) -> str:
        return str(self.value)
