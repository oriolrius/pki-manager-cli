from enum import Enum


class PostExternalSignBodyCertificateType(str, Enum):
    CLIENT = "client"
    DUAL = "dual"
    SERVER = "server"

    def __str__(self) -> str:
        return str(self.value)
