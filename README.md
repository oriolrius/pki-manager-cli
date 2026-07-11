# PKI Manager CLI

Command-line interface for managing X.509 certificates via the PKI Manager API.

## Installation

```bash
# Using uv (recommended)
uv sync
uv run pki --help

# Or install globally with pipx
pipx install .
pki --help
```

## Configuration

The CLI requires configuration to connect to the PKI Manager API. All settings are required and must be provided via environment variables, `.env` file, or CLI options.

### 1. Using `.env` File (Recommended)

```bash
cp .env.example .env
# Edit .env with your server URLs and credentials
```

The CLI looks for `.env` files in:
- Current working directory
- `~/.config/pki-cli/.env` (global configuration)

### 2. Environment Variables

```bash
export PKI_API_URL=https://your-pki-server.example.com/api/v1
export PKI_OIDC_URL=https://your-iam-server.example.com/realms/realm/protocol/openid-connect/token
export PKI_CLIENT_ID=your-client-id
export PKI_CLIENT_SECRET=your-client-secret
```

### 3. CLI Options

```bash
pki --api-url https://... --oidc-url https://... \
    --client-id your-id --client-secret your-secret \
    ca list
```

## Usage

### Check Configuration

```bash
pki config          # Show current configuration
pki login           # Test authentication
pki logout          # Clear cached token
pki health          # Check API health
```

### Certificate Authorities

```bash
pki ca list                                    # List all CAs
pki ca list --status active                    # Filter by status
pki ca get <CA_ID>                             # Get CA details
pki ca create --cn "My CA" --org "MyOrg"       # Create new CA
pki ca revoke <CA_ID> --reason key_compromise  # Revoke CA
pki ca delete <CA_ID> --force                  # Delete CA
```

### Certificates

```bash
pki cert list                                  # List all certificates
pki cert list --ca <CA_ID>                     # Filter by CA
pki cert list --type server --status active    # Filter by type and status
pki cert get <CERT_ID>                         # Get certificate details

# Issue a new certificate
pki cert issue --ca <CA_ID> --cn "example.com" --type server \
    --dns "www.example.com" --dns "api.example.com"

pki cert renew <CERT_ID>                       # Renew certificate
pki cert revoke <CERT_ID> --reason key_compromise  # Revoke
pki cert delete <CERT_ID> --force              # Delete

# Download certificate
pki cert download <CERT_ID>                    # Download as PEM
pki cert download <CERT_ID> -f pkcs12 -p pass  # Download as PKCS12
```

### SSH Certificate Manager

Manage SSH CAs, host/user certificates, principals, fleet tokens and per-host
access blocks. These use the same OIDC credentials as the X.509 commands.
`--pubkey`/`--csr` flags accept an inline value or an `@path/to/file` reference.

```bash
# CAs
pki ssh ca list                                     # List user + host CAs
pki ssh ca create --type user --label "acme-users"  # Create a CA
pki ssh ca pub <CA_ID>                              # Print the CA's OpenSSH public key
pki ssh ca krl-generate <CA_ID>                     # Rebuild the CA's KRL
pki ssh ca revocations <CA_ID>                      # List revocations

# Hosts
pki ssh host register --fqdn web1.acme.internal --pubkey @/etc/ssh/ssh_host_ecdsa_key.pub
pki ssh host issue --host-id <HOST_ID> --ttl 2592000
pki ssh host list --fqdn web1.acme.internal
pki ssh host access <HOST_ID>                       # Who can reach this host
pki ssh host cert <HOST_ID>                         # Print the host certificate
pki ssh host sshd-config <HOST_ID>                  # Print the sshd_config drop-in

# Identities & user certificates
pki ssh identity create --subject alice
pki ssh user issue --identity-id <ID> --pubkey @~/.ssh/id_ed25519.pub \
    -p admins -p developers --ttl 3600 -e permit-pty

# Principals (roles)
pki ssh principal create --name admins
pki ssh principal map --host-id <HOST_ID> --principal-id <PID> --local-account root
pki ssh principal grant --identity-id <ID> --principal-id <PID>

# Fleet tokens (automation credentials for the external SSH API)
pki ssh token mint --name ci --op sign-host --op sign-user --host-ca-id <CA_ID>
pki ssh token revoke <TOKEN_ID>

# Per-host access blocks + revocation
pki ssh block create --host-id <HOST_ID> --identity-id <ID> --reason "offboarded"
pki ssh block unblock --host-id <HOST_ID> --identity-id <ID>
pki ssh cert revoke <CERT_ID> --reason key_compromise

# Trust material & health
pki ssh trust-anchors                               # TrustedUserCAKeys / @cert-authority
pki ssh host-ca-keys                                # Host CA public key(s)
pki ssh cert-authority -p '*.acme.internal'         # known_hosts @cert-authority lines
pki ssh metrics                                     # KRL / expiry health metrics
pki ssh krl <CA_ID> -o revoked_keys                 # Download a CA's KRL bytes
```

> The public trust-material routes (`ca pub`, `host cert`, `sshd-config`,
> `host-ca-keys`, `trusted-user-ca-keys`, `cert-authority`, `krl`) are served at
> the server root, not under `/api/v1`. On deployments where a web frontend is
> mounted at the root, these may be shadowed — the CLI reports this clearly
> rather than printing the HTML page.

### External / Automation API

Machine-facing endpoints authenticated with their own bearer token (not OIDC):

- **Cluster token** (`pkimg_...`, one per CA) for the X.509 issuer API —
  `--token` or `PKI_CLUSTER_TOKEN`.
- **Fleet token** (minted via `pki ssh token mint`) for the SSH automation API —
  `--token` or `PKI_FLEET_TOKEN`.

```bash
# X.509 issuer API (cluster token)
pki external health --token pkimg_xxx
pki external ca-bundle --token pkimg_xxx --output-file ca-chain.pem
pki external sign --token pkimg_xxx --csr @request.csr --request-uid $(uuidgen)
pki external revoke --token pkimg_xxx --serial 0A1B2C

# SSH automation API (fleet token)
pki external ssh sign-host --fqdn web1.acme.internal --pubkey @/etc/ssh/ssh_host_ecdsa_key.pub
pki external ssh sign-user --subject alice --pubkey @~/.ssh/id_ed25519.pub -p admins
pki external ssh auth-principals web1.acme.internal
```

### Dashboard

```bash
pki stats                    # Show statistics
pki expiring                 # Show expiring certificates
pki search "example"         # Search CAs and certificates
```

### Output Formats

All commands support `-o json` for JSON output:

```bash
pki ca list -o json | jq '.items[].id'
```

## Examples

```bash
# Create a CA and issue a server certificate
CA_ID=$(pki ca create --cn "Internal CA" -o json | jq -r '.id')
pki cert issue --ca "$CA_ID" --cn "web.internal" --type server

# Renew expiring certificates
for id in $(pki expiring -o json | jq -r '.[].id'); do
    pki cert renew "$id"
done
```

## Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `PKI_API_URL` | PKI Manager API URL | Yes |
| `PKI_OIDC_URL` | OIDC token endpoint | Yes |
| `PKI_CLIENT_ID` | OIDC client ID | Yes |
| `PKI_CLIENT_SECRET` | OIDC client secret | Yes |
| `PKI_CLUSTER_TOKEN` | Cluster bearer token for `pki external` (X.509 issuer API) | For `external` |
| `PKI_FLEET_TOKEN` | Fleet bearer token for `pki external ssh` (SSH automation API) | For `external ssh` |

## Security Notes

- Never commit `.env` files containing credentials
- The `.gitignore` is configured to exclude `.env` files
- Use `~/.config/pki-cli/.env` for personal credentials
- Token cache is stored in `~/.cache/pki-cli/token` with restricted permissions

## Related Projects

| Project | Description |
|---------|-------------|
| [PKI Manager](https://github.com/oriolrius/pki-manager-web) | Main PKI Manager web application |
| [PKI Manager Ansible](https://github.com/oriolrius/pki-manager-ansible) | Ansible Collection for certificate management ([Galaxy](https://galaxy.ansible.com/ui/repo/published/oriolrius/pki_manager/)) |
| [PKI Manager Skill](https://github.com/oriolrius/pki-manager-skill) | Claude Code skill for AI-assisted certificate management |
