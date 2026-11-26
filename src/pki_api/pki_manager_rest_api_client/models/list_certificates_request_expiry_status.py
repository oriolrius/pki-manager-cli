from enum import Enum


class ListCertificatesRequestExpiryStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    EXPIRING_SOON = "expiring_soon"

    def __str__(self) -> str:
        return str(self.value)
