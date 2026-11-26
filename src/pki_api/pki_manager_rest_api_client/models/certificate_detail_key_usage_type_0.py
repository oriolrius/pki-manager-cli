from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CertificateDetailKeyUsageType0")


@_attrs_define
class CertificateDetailKeyUsageType0:
    """
    Attributes:
        digital_signature (bool | Unset):
        non_repudiation (bool | Unset):
        key_encipherment (bool | Unset):
        data_encipherment (bool | Unset):
        key_agreement (bool | Unset):
        key_cert_sign (bool | Unset):
        c_rl_sign (bool | Unset):
        encipher_only (bool | Unset):
        decipher_only (bool | Unset):
    """

    digital_signature: bool | Unset = UNSET
    non_repudiation: bool | Unset = UNSET
    key_encipherment: bool | Unset = UNSET
    data_encipherment: bool | Unset = UNSET
    key_agreement: bool | Unset = UNSET
    key_cert_sign: bool | Unset = UNSET
    c_rl_sign: bool | Unset = UNSET
    encipher_only: bool | Unset = UNSET
    decipher_only: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        digital_signature = self.digital_signature

        non_repudiation = self.non_repudiation

        key_encipherment = self.key_encipherment

        data_encipherment = self.data_encipherment

        key_agreement = self.key_agreement

        key_cert_sign = self.key_cert_sign

        c_rl_sign = self.c_rl_sign

        encipher_only = self.encipher_only

        decipher_only = self.decipher_only

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if digital_signature is not UNSET:
            field_dict["digitalSignature"] = digital_signature
        if non_repudiation is not UNSET:
            field_dict["nonRepudiation"] = non_repudiation
        if key_encipherment is not UNSET:
            field_dict["keyEncipherment"] = key_encipherment
        if data_encipherment is not UNSET:
            field_dict["dataEncipherment"] = data_encipherment
        if key_agreement is not UNSET:
            field_dict["keyAgreement"] = key_agreement
        if key_cert_sign is not UNSET:
            field_dict["keyCertSign"] = key_cert_sign
        if c_rl_sign is not UNSET:
            field_dict["cRLSign"] = c_rl_sign
        if encipher_only is not UNSET:
            field_dict["encipherOnly"] = encipher_only
        if decipher_only is not UNSET:
            field_dict["decipherOnly"] = decipher_only

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        digital_signature = d.pop("digitalSignature", UNSET)

        non_repudiation = d.pop("nonRepudiation", UNSET)

        key_encipherment = d.pop("keyEncipherment", UNSET)

        data_encipherment = d.pop("dataEncipherment", UNSET)

        key_agreement = d.pop("keyAgreement", UNSET)

        key_cert_sign = d.pop("keyCertSign", UNSET)

        c_rl_sign = d.pop("cRLSign", UNSET)

        encipher_only = d.pop("encipherOnly", UNSET)

        decipher_only = d.pop("decipherOnly", UNSET)

        certificate_detail_key_usage_type_0 = cls(
            digital_signature=digital_signature,
            non_repudiation=non_repudiation,
            key_encipherment=key_encipherment,
            data_encipherment=data_encipherment,
            key_agreement=key_agreement,
            key_cert_sign=key_cert_sign,
            c_rl_sign=c_rl_sign,
            encipher_only=encipher_only,
            decipher_only=decipher_only,
        )

        certificate_detail_key_usage_type_0.additional_properties = d
        return certificate_detail_key_usage_type_0

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
