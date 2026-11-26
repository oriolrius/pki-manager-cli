from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CertificateDetailIssuingCA")


@_attrs_define
class CertificateDetailIssuingCA:
    """
    Attributes:
        id (str):
        subject_dn (str):
        serial_number (str):
    """

    id: str
    subject_dn: str
    serial_number: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        subject_dn = self.subject_dn

        serial_number = self.serial_number

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "subjectDn": subject_dn,
                "serialNumber": serial_number,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        subject_dn = d.pop("subjectDn")

        serial_number = d.pop("serialNumber")

        certificate_detail_issuing_ca = cls(
            id=id,
            subject_dn=subject_dn,
            serial_number=serial_number,
        )

        certificate_detail_issuing_ca.additional_properties = d
        return certificate_detail_issuing_ca

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
