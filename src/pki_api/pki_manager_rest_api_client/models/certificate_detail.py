from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.certificate_detail_certificate_type import (
    CertificateDetailCertificateType,
)
from ..models.certificate_detail_status import CertificateDetailStatus
from ..models.certificate_detail_validity_status import CertificateDetailValidityStatus

if TYPE_CHECKING:
    from ..models.certificate_detail_basic_constraints_type_0 import (
        CertificateDetailBasicConstraintsType0,
    )
    from ..models.certificate_detail_fingerprints import CertificateDetailFingerprints
    from ..models.certificate_detail_issuer import CertificateDetailIssuer
    from ..models.certificate_detail_issuing_ca import CertificateDetailIssuingCA
    from ..models.certificate_detail_key_usage_type_0 import (
        CertificateDetailKeyUsageType0,
    )
    from ..models.certificate_detail_renewed_to_type_0_item import (
        CertificateDetailRenewedToType0Item,
    )
    from ..models.certificate_detail_subject import CertificateDetailSubject


T = TypeVar("T", bound="CertificateDetail")


@_attrs_define
class CertificateDetail:
    """
    Attributes:
        id (str):
        ca_id (str):
        serial_number (str):
        certificate_type (CertificateDetailCertificateType):
        status (CertificateDetailStatus):
        subject_dn (str):
        subject (CertificateDetailSubject):
        issuer_dn (str):
        issuer (CertificateDetailIssuer):
        not_before (datetime.datetime):
        not_after (datetime.datetime):
        validity_status (CertificateDetailValidityStatus):
        remaining_days (float | None):
        key_usage (CertificateDetailKeyUsageType0 | None):
        extended_key_usage (list[str] | None):
        san_dns (list[str] | None):
        san_ip (list[str] | None):
        san_email (list[str] | None):
        basic_constraints (CertificateDetailBasicConstraintsType0 | None):
        fingerprints (CertificateDetailFingerprints):
        issuing_ca (CertificateDetailIssuingCA):
        certificate_pem (str):
        kms_key_id (None | str):
        revocation_date (datetime.datetime | None):
        revocation_reason (None | str):
        renewed_from_id (None | str):
        renewed_to (list[CertificateDetailRenewedToType0Item] | None):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
    """

    id: str
    ca_id: str
    serial_number: str
    certificate_type: CertificateDetailCertificateType
    status: CertificateDetailStatus
    subject_dn: str
    subject: CertificateDetailSubject
    issuer_dn: str
    issuer: CertificateDetailIssuer
    not_before: datetime.datetime
    not_after: datetime.datetime
    validity_status: CertificateDetailValidityStatus
    remaining_days: float | None
    key_usage: CertificateDetailKeyUsageType0 | None
    extended_key_usage: list[str] | None
    san_dns: list[str] | None
    san_ip: list[str] | None
    san_email: list[str] | None
    basic_constraints: CertificateDetailBasicConstraintsType0 | None
    fingerprints: CertificateDetailFingerprints
    issuing_ca: CertificateDetailIssuingCA
    certificate_pem: str
    kms_key_id: None | str
    revocation_date: datetime.datetime | None
    revocation_reason: None | str
    renewed_from_id: None | str
    renewed_to: list[CertificateDetailRenewedToType0Item] | None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.certificate_detail_basic_constraints_type_0 import (
            CertificateDetailBasicConstraintsType0,
        )
        from ..models.certificate_detail_key_usage_type_0 import (
            CertificateDetailKeyUsageType0,
        )

        id = self.id

        ca_id = self.ca_id

        serial_number = self.serial_number

        certificate_type = self.certificate_type.value

        status = self.status.value

        subject_dn = self.subject_dn

        subject = self.subject.to_dict()

        issuer_dn = self.issuer_dn

        issuer = self.issuer.to_dict()

        not_before = self.not_before.isoformat()

        not_after = self.not_after.isoformat()

        validity_status = self.validity_status.value

        remaining_days: float | None
        remaining_days = self.remaining_days

        key_usage: dict[str, Any] | None
        if isinstance(self.key_usage, CertificateDetailKeyUsageType0):
            key_usage = self.key_usage.to_dict()
        else:
            key_usage = self.key_usage

        extended_key_usage: list[str] | None
        if isinstance(self.extended_key_usage, list):
            extended_key_usage = self.extended_key_usage

        else:
            extended_key_usage = self.extended_key_usage

        san_dns: list[str] | None
        if isinstance(self.san_dns, list):
            san_dns = self.san_dns

        else:
            san_dns = self.san_dns

        san_ip: list[str] | None
        if isinstance(self.san_ip, list):
            san_ip = self.san_ip

        else:
            san_ip = self.san_ip

        san_email: list[str] | None
        if isinstance(self.san_email, list):
            san_email = self.san_email

        else:
            san_email = self.san_email

        basic_constraints: dict[str, Any] | None
        if isinstance(self.basic_constraints, CertificateDetailBasicConstraintsType0):
            basic_constraints = self.basic_constraints.to_dict()
        else:
            basic_constraints = self.basic_constraints

        fingerprints = self.fingerprints.to_dict()

        issuing_ca = self.issuing_ca.to_dict()

        certificate_pem = self.certificate_pem

        kms_key_id: None | str
        kms_key_id = self.kms_key_id

        revocation_date: None | str
        if isinstance(self.revocation_date, datetime.datetime):
            revocation_date = self.revocation_date.isoformat()
        else:
            revocation_date = self.revocation_date

        revocation_reason: None | str
        revocation_reason = self.revocation_reason

        renewed_from_id: None | str
        renewed_from_id = self.renewed_from_id

        renewed_to: list[dict[str, Any]] | None
        if isinstance(self.renewed_to, list):
            renewed_to = []
            for renewed_to_type_0_item_data in self.renewed_to:
                renewed_to_type_0_item = renewed_to_type_0_item_data.to_dict()
                renewed_to.append(renewed_to_type_0_item)

        else:
            renewed_to = self.renewed_to

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "caId": ca_id,
                "serialNumber": serial_number,
                "certificateType": certificate_type,
                "status": status,
                "subjectDn": subject_dn,
                "subject": subject,
                "issuerDn": issuer_dn,
                "issuer": issuer,
                "notBefore": not_before,
                "notAfter": not_after,
                "validityStatus": validity_status,
                "remainingDays": remaining_days,
                "keyUsage": key_usage,
                "extendedKeyUsage": extended_key_usage,
                "sanDns": san_dns,
                "sanIp": san_ip,
                "sanEmail": san_email,
                "basicConstraints": basic_constraints,
                "fingerprints": fingerprints,
                "issuingCA": issuing_ca,
                "certificatePem": certificate_pem,
                "kmsKeyId": kms_key_id,
                "revocationDate": revocation_date,
                "revocationReason": revocation_reason,
                "renewedFromId": renewed_from_id,
                "renewedTo": renewed_to,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.certificate_detail_basic_constraints_type_0 import (
            CertificateDetailBasicConstraintsType0,
        )
        from ..models.certificate_detail_fingerprints import (
            CertificateDetailFingerprints,
        )
        from ..models.certificate_detail_issuer import CertificateDetailIssuer
        from ..models.certificate_detail_issuing_ca import CertificateDetailIssuingCA
        from ..models.certificate_detail_key_usage_type_0 import (
            CertificateDetailKeyUsageType0,
        )
        from ..models.certificate_detail_renewed_to_type_0_item import (
            CertificateDetailRenewedToType0Item,
        )
        from ..models.certificate_detail_subject import CertificateDetailSubject

        d = dict(src_dict)
        id = d.pop("id")

        ca_id = d.pop("caId")

        serial_number = d.pop("serialNumber")

        certificate_type = CertificateDetailCertificateType(d.pop("certificateType"))

        status = CertificateDetailStatus(d.pop("status"))

        subject_dn = d.pop("subjectDn")

        subject = CertificateDetailSubject.from_dict(d.pop("subject"))

        issuer_dn = d.pop("issuerDn")

        issuer = CertificateDetailIssuer.from_dict(d.pop("issuer"))

        not_before = isoparse(d.pop("notBefore"))

        not_after = isoparse(d.pop("notAfter"))

        validity_status = CertificateDetailValidityStatus(d.pop("validityStatus"))

        def _parse_remaining_days(data: object) -> float | None:
            if data is None:
                return data
            return cast(float | None, data)

        remaining_days = _parse_remaining_days(d.pop("remainingDays"))

        def _parse_key_usage(data: object) -> CertificateDetailKeyUsageType0 | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                key_usage_type_0 = CertificateDetailKeyUsageType0.from_dict(data)

                return key_usage_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CertificateDetailKeyUsageType0 | None, data)

        key_usage = _parse_key_usage(d.pop("keyUsage"))

        def _parse_extended_key_usage(data: object) -> list[str] | None:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                extended_key_usage_type_0 = cast(list[str], data)

                return extended_key_usage_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None, data)

        extended_key_usage = _parse_extended_key_usage(d.pop("extendedKeyUsage"))

        def _parse_san_dns(data: object) -> list[str] | None:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                san_dns_type_0 = cast(list[str], data)

                return san_dns_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None, data)

        san_dns = _parse_san_dns(d.pop("sanDns"))

        def _parse_san_ip(data: object) -> list[str] | None:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                san_ip_type_0 = cast(list[str], data)

                return san_ip_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None, data)

        san_ip = _parse_san_ip(d.pop("sanIp"))

        def _parse_san_email(data: object) -> list[str] | None:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                san_email_type_0 = cast(list[str], data)

                return san_email_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None, data)

        san_email = _parse_san_email(d.pop("sanEmail"))

        def _parse_basic_constraints(
            data: object,
        ) -> CertificateDetailBasicConstraintsType0 | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                basic_constraints_type_0 = (
                    CertificateDetailBasicConstraintsType0.from_dict(data)
                )

                return basic_constraints_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CertificateDetailBasicConstraintsType0 | None, data)

        basic_constraints = _parse_basic_constraints(d.pop("basicConstraints"))

        fingerprints = CertificateDetailFingerprints.from_dict(d.pop("fingerprints"))

        issuing_ca = CertificateDetailIssuingCA.from_dict(d.pop("issuingCA"))

        certificate_pem = d.pop("certificatePem")

        def _parse_kms_key_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        kms_key_id = _parse_kms_key_id(d.pop("kmsKeyId"))

        def _parse_revocation_date(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                revocation_date_type_0 = isoparse(data)

                return revocation_date_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        revocation_date = _parse_revocation_date(d.pop("revocationDate"))

        def _parse_revocation_reason(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        revocation_reason = _parse_revocation_reason(d.pop("revocationReason"))

        def _parse_renewed_from_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        renewed_from_id = _parse_renewed_from_id(d.pop("renewedFromId"))

        def _parse_renewed_to(
            data: object,
        ) -> list[CertificateDetailRenewedToType0Item] | None:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                renewed_to_type_0 = []
                _renewed_to_type_0 = data
                for renewed_to_type_0_item_data in _renewed_to_type_0:
                    renewed_to_type_0_item = (
                        CertificateDetailRenewedToType0Item.from_dict(
                            renewed_to_type_0_item_data
                        )
                    )

                    renewed_to_type_0.append(renewed_to_type_0_item)

                return renewed_to_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[CertificateDetailRenewedToType0Item] | None, data)

        renewed_to = _parse_renewed_to(d.pop("renewedTo"))

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        certificate_detail = cls(
            id=id,
            ca_id=ca_id,
            serial_number=serial_number,
            certificate_type=certificate_type,
            status=status,
            subject_dn=subject_dn,
            subject=subject,
            issuer_dn=issuer_dn,
            issuer=issuer,
            not_before=not_before,
            not_after=not_after,
            validity_status=validity_status,
            remaining_days=remaining_days,
            key_usage=key_usage,
            extended_key_usage=extended_key_usage,
            san_dns=san_dns,
            san_ip=san_ip,
            san_email=san_email,
            basic_constraints=basic_constraints,
            fingerprints=fingerprints,
            issuing_ca=issuing_ca,
            certificate_pem=certificate_pem,
            kms_key_id=kms_key_id,
            revocation_date=revocation_date,
            revocation_reason=revocation_reason,
            renewed_from_id=renewed_from_id,
            renewed_to=renewed_to,
            created_at=created_at,
            updated_at=updated_at,
        )

        certificate_detail.additional_properties = d
        return certificate_detail

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
