from enum import Enum


class GetAuditResponse200ItemsItemActorTypeType2Type1(str, Enum):
    ANONYMOUS = "anonymous"
    INTEGRATION = "integration"
    SSH_TOKEN = "ssh_token"
    USER = "user"

    def __str__(self) -> str:
        return str(self.value)
