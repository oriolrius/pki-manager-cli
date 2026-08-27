# PKI Manager CLI

Command-line interface for the PKI Manager API — X.509 certificate authorities and
certificates, CRLs, the SSH Certificate Manager, bulk operations, the audit log and
the machine-facing issuer APIs.

**Coverage:** every operation in the server's OpenAPI document (`/api/v1/openapi.json`)
has a corresponding command, plus the unauthenticated trust-material routes served at
the server root. See [Command ↔ endpoint map](#command--endpoint-map).

| pki-cli | PKI Manager | REST API |
|---------|-------------|----------|
| 0.3.0   | 3.9.5       | v1.0.0   |

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

Only `PKI_API_URL` is mandatory. For authentication, pick one of three modes:

1. **OIDC client credentials** (normal) — set `PKI_OIDC_URL`, `PKI_CLIENT_ID` and
   `PKI_CLIENT_SECRET` together. The CLI exchanges them for a token and caches it.
2. **Pre-obtained bearer token** — set `PKI_TOKEN` (or `--token`) to skip the OIDC
   exchange, e.g. when a CI step already minted a token.
3. **Anonymous** — leave all of the above unset. This only works against a deployment
   running with `OIDC_ENABLED=false`, typically a local dev stack.

Settings come from environment variables, a `.env` file, or CLI options (in increasing
order of precedence). Run `pki config` to see which mode is active.

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

# ...or a pre-obtained token instead of the three OIDC values
export PKI_TOKEN=eyJhbGciOi...

# ...or nothing at all, against a dev server with OIDC disabled
export PKI_API_URL=http://localhost:52081/api/v1
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
pki ca list --status active --search acme      # Filter and search
pki ca list --sort-by expiryDate --sort-order asc --limit 20 --offset 20
pki ca get <CA_ID>                             # Get CA details
pki ca create --cn "My CA" --org "MyOrg" --validity-years 10
pki ca certs <CA_ID> --status active           # Certificates issued by this CA
pki ca revoke <CA_ID> --reason keyCompromise   # Revoke CA
pki ca delete <CA_ID> --destroy-key --force    # Delete CA (and its KMS key)

# Download the CA certificate / a truststore bundle
pki ca download <CA_ID> --format pem -o ca.pem
pki ca download <CA_ID> --format p12-truststore --password pass -o truststore.p12
pki ca pem <CA_ID>                             # Public AIA URL, no credentials needed
```

Revocation reasons are the RFC 5280 camelCase codes: `unspecified`, `keyCompromise`,
`caCompromise`, `affiliationChanged`, `superseded`, `cessationOfOperation`,
`certificateHold`, `removeFromCRL`.

### Certificates

```bash
pki cert list                                  # List all certificates
pki cert list --ca <CA_ID>                     # Filter by CA
pki cert list --type server --status active    # Filter by type and status
pki cert list --search example.com --sort-by notAfter --sort-order asc
pki cert get <CERT_ID>                         # Get certificate details

# Issue a new certificate (the CN is added to the DNS SANs automatically)
pki cert issue --ca <CA_ID> --cn "example.com" --type server \
    --dns "www.example.com" --dns "api.example.com" \
    --ip 10.0.0.1 --email admin@example.com --ou Platform --tag prod

pki cert renew <CERT_ID> --validity 365        # Renew certificate
pki cert renew <CERT_ID> --same-key --revoke-original
pki cert renew <CERT_ID> --cn new.example.com  # Renew with an updated subject
pki cert revoke <CERT_ID> --reason keyCompromise --generate-crl
pki cert delete <CERT_ID> --destroy-key --force

# Download certificate
pki cert download <CERT_ID>                    # PEM (default)
pki cert download <CERT_ID> -f chain-pem       # Certificate + issuing chain
pki cert download <CERT_ID> -f key-pem         # Private key
pki cert download <CERT_ID> -f full-pem        # Certificate + key + chain
pki cert download <CERT_ID> -f p12 -p secret   # PKCS#12 keystore
pki cert download <CERT_ID> -f jks-keystore -p secret
```

Download formats: `pem`, `der`, `chain-pem`, `full-pem`, `full-der`, `csr-pem`,
`key-pem`, `key-der`, `pkcs8-pem`, `pkcs8-der`, `pkcs8-encrypted`, `p12`/`pfx`,
`jks-keystore`, `jks-truststore`.

### Bulk Operations

Up to 100 certificates per call. IDs come from repeatable `--id` flags, a
comma-separated list, or `--ids-file` (one per line, `-` for stdin).

```bash
# Issue from a headerless CSV: certificateType,CN,O,C,SANs,validityDays
# (SANs are ';'-separated and auto-classified into DNS / IP / email)
printf 'server,web1.acme.io,Acme,ES,web1.acme.io;10.0.0.1,365\n' > certs.csv
pki cert bulk issue --ca <CA_ID> --csv certs.csv

pki cert list --status active -o json | jq -r '.items[].id' > ids.txt
pki cert bulk renew --ids-file ids.txt --validity 90
pki cert bulk revoke --ids-file ids.txt --reason superseded --force
pki cert bulk delete --ids-file ids.txt --destroy-key --force
pki cert bulk download --ids-file ids.txt --format pem --output-file bundle.zip
```

`bulk` commands exit non-zero if any item failed, and print the per-item result.

### Certificate Revocation Lists

```bash
pki crl list <CA_ID>                           # CRLs this CA has published
pki crl generate <CA_ID> --next-update-days 14 # Publish a new CRL
pki crl download <CA_ID> -o ca.crl             # Public CDP download (PEM)
pki crl download <CA_ID> --format der -o ca.der
```

### Domains, Audit Log and Reports

```bash
pki domain list --search acme.io               # Domain inventory from cert SANs
pki domain list --ca <CA_ID> --limit 100

pki audit list --limit 50                      # Tamper-evident operation log
pki audit list --operation ca.create --status failure
pki audit list --entity-type certificate --entity-id <CERT_ID>
pki audit list --start 2026-01-01 --end 2026-06-30   # ISO date or Unix timestamp

pki report generate --type certificate_inventory --output-file inventory.csv
pki report generate --type revocation --ca <CA_ID> --start 2026-01-01
pki report generate --type ca_operations -o json
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
pki ssh host auth-principals <HOST_ID>              # Render AuthorizedPrincipalsFile contents
pki ssh host mark-pushed <HOST_ID>                  # Clear Stale after pushing those files
pki ssh host blocks <HOST_ID>                       # Block history (active + lifted)

# Identities & user certificates
pki ssh identity create --subject alice
pki ssh identity blocks <ID>                        # Active blocks + distribution state
pki ssh identity collisions <ID>                    # Identities sharing a certified key
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
pki ssh block fleet                                 # Fleet-wide block + KRL distribution
pki ssh cert revoke <CERT_ID> --reason "key compromise"

# Trust material & health
pki ssh trust-anchors                               # TrustedUserCAKeys / @cert-authority
pki ssh host-ca-keys                                # Host CA public key(s)
pki ssh cert-authority -p '*.acme.internal'         # known_hosts @cert-authority lines
pki ssh metrics                                     # KRL / expiry health metrics
pki ssh trusted-user-ca-keys                        # TrustedUserCAKeys file contents
pki ssh krl <CA_ID> -o revoked_keys                 # Download a CA's public KRL bytes
pki ssh ca krl <CA_ID> -o revoked_keys              # Same, authenticated
pki ssh krl-host <HOST_ID>                          # A host's composed public KRL
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
pki external ssh register-host-pubkey --fqdn web1.acme.internal
pki external ssh auth-principals web1.acme.internal
pki external ssh krl --host-id web1.acme.internal -o krl.enc   # ECIES envelope, no token
```

### Dashboard

```bash
pki health                   # API health + version
pki stats                    # Show statistics
pki expiring --limit 20      # Show expiring certificates
pki search "example"         # Search CAs, certificates and domains
```

### Output Formats

All commands support `-o json` for JSON output. Status lines (`✓`/`✗`/notes) go to
stderr, so JSON output pipes cleanly:

```bash
pki ca list -o json | jq -r '.items[].id'
```

## Examples

```bash
# Create a CA and issue a server certificate
CA_ID=$(pki ca create --cn "Internal CA" -o json | jq -r '.id')
pki cert issue --ca "$CA_ID" --cn "web.internal" --type server

# Renew every certificate expiring soon, in one call
pki expiring --limit 20 -o json | jq -r '.[] | select(.type=="Server") | .id' > ids.txt
pki cert bulk renew --ids-file ids.txt --validity 365

# Rotate a CA's CRL and publish it to a distribution point
pki crl generate "$CA_ID" --next-update-days 7
pki crl download "$CA_ID" -o /var/www/crl/internal.crl

# Bootstrap trust on a new host without credentials
pki ca pem "$CA_ID" > /usr/local/share/ca-certificates/internal.crt

# Who touched this certificate?
pki audit list --entity-type certificate --entity-id "$CERT_ID"

# Quarterly compliance evidence
pki report generate --type certificate_inventory --output-file q3-inventory.csv
```

## Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `PKI_API_URL` | PKI Manager API URL | Yes |
| `PKI_OIDC_URL` | OIDC token endpoint | With OIDC auth |
| `PKI_CLIENT_ID` | OIDC client ID | With OIDC auth |
| `PKI_CLIENT_SECRET` | OIDC client secret | With OIDC auth |
| `PKI_TOKEN` | Pre-obtained bearer token (alternative to the three OIDC values) | No |
| `PKI_CLUSTER_TOKEN` | Cluster bearer token for `pki external` (X.509 issuer API) | For `external` |
| `PKI_FLEET_TOKEN` | Fleet bearer token for `pki external ssh` (SSH automation API) | For `external ssh` |

## Command ↔ endpoint map

Every operation in the server's OpenAPI document is reachable from the CLI.
Regenerate this table (and verify coverage) after a server upgrade — see
[Keeping up with the server](#keeping-up-with-the-server).

**Dashboard**

| Endpoint | Command |
|----------|---------|
| `GET /dashboard/expiring` | `pki expiring` |
| `GET /dashboard/stats` | `pki stats` |
| `GET /health` | `pki health` |

**Search**

| Endpoint | Command |
|----------|---------|
| `GET /search` | `pki search` |

**Certificate Authorities**

| Endpoint | Command |
|----------|---------|
| `GET /cas/` | `pki ca list` |
| `POST /cas/` | `pki ca create` |
| `GET /cas/{id}` | `pki ca get` |
| `DELETE /cas/{id}` | `pki ca delete` |
| `GET /cas/{id}/certificates` | `pki ca certs` |
| `GET /cas/{id}/crls` | `pki crl list` |
| `POST /cas/{id}/crls` | `pki crl generate` |
| `GET /cas/{id}/download` | `pki ca download` |
| `POST /cas/{id}/revoke` | `pki ca revoke` |

**Certificates**

| Endpoint | Command |
|----------|---------|
| `GET /certificates/` | `pki cert list` |
| `POST /certificates/` | `pki cert issue` |
| `GET /certificates/{id}` | `pki cert get` |
| `DELETE /certificates/{id}` | `pki cert delete` |
| `GET /certificates/{id}/download` | `pki cert download` |
| `POST /certificates/{id}/renew` | `pki cert renew` |
| `POST /certificates/{id}/revoke` | `pki cert revoke` |

**Bulk Operations**

| Endpoint | Command |
|----------|---------|
| `DELETE /certificates/bulk/` | `pki cert bulk delete` |
| `POST /certificates/bulk/download` | `pki cert bulk download` |
| `POST /certificates/bulk/issue` | `pki cert bulk issue` |
| `POST /certificates/bulk/renew` | `pki cert bulk renew` |
| `POST /certificates/bulk/revoke` | `pki cert bulk revoke` |

**Domains**

| Endpoint | Command |
|----------|---------|
| `GET /domains` | `pki domain list` |

**Audit**

| Endpoint | Command |
|----------|---------|
| `GET /audit` | `pki audit list` |
| `POST /reports` | `pki report generate` |

**SSH Certificate Manager**

| Endpoint | Command |
|----------|---------|
| `POST /ssh/blocks` | `pki ssh block create` |
| `GET /ssh/blocks/fleet` | `pki ssh block fleet` |
| `POST /ssh/blocks/unblock` | `pki ssh block unblock` |
| `GET /ssh/cas` | `pki ssh ca list` |
| `POST /ssh/cas` | `pki ssh ca create` |
| `POST /ssh/cas/{caId}/krl` | `pki ssh ca krl-generate` |
| `GET /ssh/cas/{caId}/krl.bin` | `pki ssh ca krl` |
| `GET /ssh/cas/{caId}/revocations` | `pki ssh ca revocations` |
| `POST /ssh/certs/{id}/revoke` | `pki ssh cert revoke` |
| `GET /ssh/hosts` | `pki ssh host list` |
| `POST /ssh/hosts` | `pki ssh host register` |
| `POST /ssh/hosts/issue` | `pki ssh host issue` |
| `GET /ssh/hosts/{id}/access` | `pki ssh host access` |
| `GET /ssh/hosts/{id}/auth-principals` | `pki ssh host auth-principals` |
| `POST /ssh/hosts/{id}/auth-principals/pushed` | `pki ssh host mark-pushed` |
| `GET /ssh/hosts/{id}/blocks` | `pki ssh host blocks` |
| `POST /ssh/identities` | `pki ssh identity create` |
| `GET /ssh/identities/{id}/blocks` | `pki ssh identity blocks` |
| `GET /ssh/identities/{id}/collisions` | `pki ssh identity collisions` |
| `GET /ssh/metrics` | `pki ssh metrics` |
| `GET /ssh/principals` | `pki ssh principal list` |
| `POST /ssh/principals` | `pki ssh principal create` |
| `POST /ssh/principals/grant` | `pki ssh principal grant` |
| `POST /ssh/principals/map` | `pki ssh principal map` |
| `GET /ssh/tokens` | `pki ssh token list` |
| `POST /ssh/tokens` | `pki ssh token mint` |
| `POST /ssh/tokens/{id}/revoke` | `pki ssh token revoke` |
| `GET /ssh/trust-anchors` | `pki ssh trust-anchors` |
| `POST /ssh/users/issue` | `pki ssh user issue` |

**External Issuer**

| Endpoint | Command |
|----------|---------|
| `GET /external/ca-bundle` | `pki external ca-bundle` |
| `GET /external/health` | `pki external health` |
| `POST /external/revoke` | `pki external revoke` |
| `POST /external/sign` | `pki external sign` |

**SSH External Issuer**

| Endpoint | Command |
|----------|---------|
| `GET /external/ssh/hosts/{fqdn}/auth-principals` | `pki external ssh auth-principals` |
| `POST /external/ssh/krl` | `pki external ssh krl` |
| `POST /external/ssh/register-host-pubkey` | `pki external ssh register-host-pubkey` |
| `POST /external/ssh/sign-host` | `pki external ssh sign-host` |
| `POST /external/ssh/sign-user` | `pki external ssh sign-user` |

**Public routes** (served at the server root, not under `/api/v1`, and marked
`hide: true` so they do not appear in the OpenAPI document):

| Endpoint | Command |
|----------|---------|
| `GET /cas/{caId}.{format}` | `pki ca pem` |
| `GET /crl/{caId}.{format}` | `pki crl download` |
| `GET /krl/{caId}.{bin,json}` | `pki ssh krl` |
| `GET /krl/hosts/{hostId}.{bin,json}` | `pki ssh krl-host` |
| `GET /ssh/cas/{id}/ca.pub` | `pki ssh ca pub` |
| `GET /ssh/cert-authority` | `pki ssh cert-authority` |
| `GET /ssh/host-ca-keys` | `pki ssh host-ca-keys` |
| `GET /ssh/hosts/{id}/cert.pub` | `pki ssh host cert` |
| `GET /ssh/hosts/{id}/sshd-config` | `pki ssh host sshd-config` |
| `GET /ssh/trusted-user-ca-keys` | `pki ssh trusted-user-ca-keys` |

## Keeping up with the server

`src/pki_api/` is generated from the server's OpenAPI document and `openapi.json`
is the copy it was generated from. After a PKI Manager upgrade:

```bash
curl -s "$PKI_API_URL/openapi.json" -o openapi.json
uv run openapi-python-client generate --path openapi.json --meta none \
    --output-path /tmp/gen --overwrite
rm -rf src/pki_api/pki_manager_rest_api_client
cp -r /tmp/gen src/pki_api/pki_manager_rest_api_client
touch src/pki_api/pki_manager_rest_api_client/py.typed
```

Then diff `openapi.json` against the previous revision for new or changed
operations, add commands for anything new, and bump `PKI_MANAGER_VERSION` in
`src/pki_cli/__init__.py`.

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
