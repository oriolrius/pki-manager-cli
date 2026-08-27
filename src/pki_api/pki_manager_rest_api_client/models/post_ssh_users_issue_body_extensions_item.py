from enum import Enum


class PostSshUsersIssueBodyExtensionsItem(str, Enum):
    PERMIT_AGENT_FORWARDING = "permit-agent-forwarding"
    PERMIT_PORT_FORWARDING = "permit-port-forwarding"
    PERMIT_PTY = "permit-pty"
    PERMIT_USER_RC = "permit-user-rc"
    PERMIT_X11_FORWARDING = "permit-X11-forwarding"

    def __str__(self) -> str:
        return str(self.value)
