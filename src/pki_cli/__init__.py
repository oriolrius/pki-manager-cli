"""PKI CLI - Command line tool for PKI Manager API."""

__version__ = "0.4.0"

# The PKI Manager release this CLI was generated and verified against. The
# bundled OpenAPI client in ``pki_api`` mirrors that release's
# ``/api/v1/openapi.json`` exactly, so a newer server may expose endpoints this
# CLI does not know about yet.
#
# NOTE: the 22 SSH lifecycle endpoints added in pki-cli 0.4.0 (SSH REST/tRPC
# parity, PKI Manager TASK-216) landed after the 3.9.5 tag. Against a server
# that predates them, ``pki ssh {ca get,ca import,ca rotate,ca retire,ca revoke,
# ca revoke-serial,ca revoke-key,host get,host deploy-bundle,host revoke,
# host ecies-key,host offboard,identity list,identity disable,identity offboard,
# user certificates,principal mappings,principal stale-hosts,principal delete,
# bulk expiring,bulk renew,bulk revoke}`` return 404; every other command works.
PKI_MANAGER_VERSION = "3.9.5"
API_VERSION = "1.0.0"
