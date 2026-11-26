from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.bulk_revoke_certificates_request_reason import (
    BulkRevokeCertificatesRequestReason,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="BulkRevokeCertificatesRequest")


@_attrs_define
class BulkRevokeCertificatesRequest:
    """
    Attributes:
        certificate_ids (list[str]):
        reason (BulkRevokeCertificatesRequestReason):
        details (str | Unset):
        generate_crl (bool | Unset):  Default: True.
    """

    certificate_ids: list[str]
    reason: BulkRevokeCertificatesRequestReason
    details: str | Unset = UNSET
    generate_crl: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        certificate_ids = self.certificate_ids

        reason = self.reason.value

        details = self.details

        generate_crl = self.generate_crl

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "certificateIds": certificate_ids,
                "reason": reason,
            }
        )
        if details is not UNSET:
            field_dict["details"] = details
        if generate_crl is not UNSET:
            field_dict["generateCrl"] = generate_crl

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        certificate_ids = cast(list[str], d.pop("certificateIds"))

        reason = BulkRevokeCertificatesRequestReason(d.pop("reason"))

        details = d.pop("details", UNSET)

        generate_crl = d.pop("generateCrl", UNSET)

        bulk_revoke_certificates_request = cls(
            certificate_ids=certificate_ids,
            reason=reason,
            details=details,
            generate_crl=generate_crl,
        )

        bulk_revoke_certificates_request.additional_properties = d
        return bulk_revoke_certificates_request

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
