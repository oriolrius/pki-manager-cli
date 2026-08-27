from enum import Enum


class PostSshTokensBodyOpSetItem(str, Enum):
    GET_PRINCIPALS = "get-principals"
    REGISTER_HOST_PUBKEY = "register-host-pubkey"
    SIGN_HOST = "sign-host"
    SIGN_USER = "sign-user"

    def __str__(self) -> str:
        return str(self.value)
