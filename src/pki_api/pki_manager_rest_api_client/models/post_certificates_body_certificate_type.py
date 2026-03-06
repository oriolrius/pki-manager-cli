from enum import Enum


class PostCertificatesBodyCertificateType(str, Enum):
    CLIENT = "client"
    CODE_SIGNING = "code_signing"
    DUAL = "dual"
    EMAIL = "email"
    SERVER = "server"

    def __str__(self) -> str:
        return str(self.value)
