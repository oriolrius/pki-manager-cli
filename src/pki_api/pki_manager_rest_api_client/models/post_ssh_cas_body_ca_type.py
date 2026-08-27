from enum import Enum


class PostSshCasBodyCaType(str, Enum):
    HOST = "host"
    USER = "user"

    def __str__(self) -> str:
        return str(self.value)
