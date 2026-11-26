from enum import Enum


class PostExternalRevokeResponse200Status(str, Enum):
    REVOKED = "revoked"

    def __str__(self) -> str:
        return str(self.value)
