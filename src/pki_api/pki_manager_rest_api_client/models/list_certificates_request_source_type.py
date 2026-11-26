from enum import Enum


class ListCertificatesRequestSourceType(str, Enum):
    INTEGRATION = "integration"
    K8S = "k8s"
    MANUAL = "manual"
    SCEP = "scep"

    def __str__(self) -> str:
        return str(self.value)
