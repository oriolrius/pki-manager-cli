"""The renderers must survive both response shapes the API actually returns.

List endpoints return a flat ``subject`` string and ``certificateCount``; detail
endpoints return a structured ``subject`` object, ``subjectDn`` and
``issuedCertificateCount``. Rendering either must not raise.
"""

from __future__ import annotations

from pki_cli.output import (
    print_ca_detail,
    print_ca_table,
    print_cert_detail,
    print_cert_table,
    print_stats,
    subject_of,
)

CA_LIST_ITEM = {
    "id": "19fa0fbe-3496-4ef7-acd3-44d1c3c3b77b",
    "subject": "CN=Internal CA,O=Acme,C=ES",
    "serialNumber": "65831b07",
    "keyAlgorithm": "RSA-4096",
    "notBefore": "2026-06-27T07:39:00.000Z",
    "notAfter": "2036-06-27T07:39:00.000Z",
    "status": "active",
    "certificateCount": 3,
    "createdAt": "2026-06-27T07:39:00.000Z",
}

CA_DETAIL = {
    "id": "19fa0fbe-3496-4ef7-acd3-44d1c3c3b77b",
    "subject": {"commonName": "Internal CA", "organization": "Acme", "country": "ES"},
    "subjectDn": "CN=Internal CA,O=Acme,C=ES",
    "issuer": {},
    "issuerDn": "CN=Internal CA,O=Acme,C=ES",
    "serialNumber": "65831b07",
    "keyAlgorithm": "RSA-4096",
    "notBefore": "2026-06-27T07:39:00.000Z",
    "notAfter": "2036-06-27T07:39:00.000Z",
    "validityStatus": "valid",
    "status": "active",
    "extensions": {},
    "fingerprints": {"sha256": "AD:E9:47", "sha1": "45:41:B3"},
    "issuedCertificateCount": 3,
    "revocationDate": None,
    "revocationReason": None,
    "createdAt": "2026-06-27T07:39:00.000Z",
}

CERT_LIST_ITEM = {
    "id": "265a12cc-3b10-46cb-9e02-1387d0767e76",
    "caId": "19fa0fbe-3496-4ef7-acd3-44d1c3c3b77b",
    "subjectDn": "CN=web.internal,O=Acme,C=ES",
    "serialNumber": "3486e729",
    "certificateType": "server",
    "notBefore": "2026-06-29T17:15:57.000Z",
    "notAfter": "2027-06-29T17:15:57.000Z",
    "status": "active",
    "expiryStatus": "active",
    "sanDns": ["web.internal"],
    "sanIp": None,
    "sanEmail": None,
    "createdAt": "2026-06-29T17:15:57.000Z",
}

CERT_DETAIL = {
    **CERT_LIST_ITEM,
    "subject": {},
    "issuerDn": "CN=Internal CA,O=Acme,C=ES",
    "issuer": {},
    "validityStatus": "valid",
    "remainingDays": 307,
    "keyUsage": None,
    "extendedKeyUsage": ["serverAuth"],
    "basicConstraints": {},
    "fingerprints": {"sha256": "13:42:CC", "sha1": "9A:BB:CC"},
    "issuingCA": {"id": "19fa0fbe", "subjectDn": "CN=Internal CA", "serialNumber": "6583"},
    "kmsKeyId": "34d66eb7",
    "revocationDate": None,
    "revocationReason": None,
    "renewedFromId": None,
    "renewedTo": None,
    "updatedAt": "2026-06-29T17:15:57.000Z",
}


def test_subject_of_accepts_both_shapes():
    assert subject_of(CA_LIST_ITEM) == "CN=Internal CA,O=Acme,C=ES"
    assert subject_of(CA_DETAIL) == "CN=Internal CA,O=Acme,C=ES"
    # Detail shape with only the structured object still renders a DN.
    assert subject_of({"subject": {"commonName": "a", "country": "ES"}}) == "CN=a,C=ES"
    assert subject_of({}) == "-"


def test_ca_renderers_do_not_raise():
    print_ca_table([CA_LIST_ITEM])
    print_ca_detail(CA_DETAIL)
    print_ca_detail(CA_LIST_ITEM)


def test_cert_renderers_do_not_raise():
    print_cert_table([CERT_LIST_ITEM])
    print_cert_detail(CERT_DETAIL)
    print_cert_detail(CERT_LIST_ITEM)


def test_stats_uses_the_api_key_casing(capsys):
    """The API returns totalCAs/activeCAs, not totalCas/activeCas."""
    print_stats({"totalCAs": 17, "activeCAs": 16, "totalCertificates": 8, "activeCertificates": 7})
    out = capsys.readouterr().out
    assert "17" in out and "16" in out


def test_stats_surfaces_unknown_keys(capsys):
    print_stats({"totalCAs": 1, "somethingNew": 42})
    assert "somethingNew" in capsys.readouterr().out
