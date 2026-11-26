from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetExternalCaBundleResponse200")


@_attrs_define
class GetExternalCaBundleResponse200:
    """
    Attributes:
        ca_id (str | Unset):
        subject_dn (str | Unset):
        certificate_pem (str | Unset):
        chain_pem (str | Unset):
    """

    ca_id: str | Unset = UNSET
    subject_dn: str | Unset = UNSET
    certificate_pem: str | Unset = UNSET
    chain_pem: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ca_id = self.ca_id

        subject_dn = self.subject_dn

        certificate_pem = self.certificate_pem

        chain_pem = self.chain_pem

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if ca_id is not UNSET:
            field_dict["caId"] = ca_id
        if subject_dn is not UNSET:
            field_dict["subjectDn"] = subject_dn
        if certificate_pem is not UNSET:
            field_dict["certificatePem"] = certificate_pem
        if chain_pem is not UNSET:
            field_dict["chainPem"] = chain_pem

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ca_id = d.pop("caId", UNSET)

        subject_dn = d.pop("subjectDn", UNSET)

        certificate_pem = d.pop("certificatePem", UNSET)

        chain_pem = d.pop("chainPem", UNSET)

        get_external_ca_bundle_response_200 = cls(
            ca_id=ca_id,
            subject_dn=subject_dn,
            certificate_pem=certificate_pem,
            chain_pem=chain_pem,
        )

        get_external_ca_bundle_response_200.additional_properties = d
        return get_external_ca_bundle_response_200

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
