from enum import Enum


class ListCertificatesRequestType1SourceType(str, Enum):
    K8S = "k8s"
    MANUAL = "manual"

    def __str__(self) -> str:
        return str(self.value)
