from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostExternalSignResponse200")


@_attrs_define
class PostExternalSignResponse200:
    """
    Attributes:
        idempotent (bool | Unset):
        id (str | Unset):
        serial_number (str | Unset):
        certificate_pem (str | Unset):
        chain_pem (str | Unset):
        not_before (datetime.datetime | Unset):
        not_after (datetime.datetime | Unset):
    """

    idempotent: bool | Unset = UNSET
    id: str | Unset = UNSET
    serial_number: str | Unset = UNSET
    certificate_pem: str | Unset = UNSET
    chain_pem: str | Unset = UNSET
    not_before: datetime.datetime | Unset = UNSET
    not_after: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        idempotent = self.idempotent

        id = self.id

        serial_number = self.serial_number

        certificate_pem = self.certificate_pem

        chain_pem = self.chain_pem

        not_before: str | Unset = UNSET
        if not isinstance(self.not_before, Unset):
            not_before = self.not_before.isoformat()

        not_after: str | Unset = UNSET
        if not isinstance(self.not_after, Unset):
            not_after = self.not_after.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if idempotent is not UNSET:
            field_dict["idempotent"] = idempotent
        if id is not UNSET:
            field_dict["id"] = id
        if serial_number is not UNSET:
            field_dict["serialNumber"] = serial_number
        if certificate_pem is not UNSET:
            field_dict["certificatePem"] = certificate_pem
        if chain_pem is not UNSET:
            field_dict["chainPem"] = chain_pem
        if not_before is not UNSET:
            field_dict["notBefore"] = not_before
        if not_after is not UNSET:
            field_dict["notAfter"] = not_after

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        idempotent = d.pop("idempotent", UNSET)

        id = d.pop("id", UNSET)

        serial_number = d.pop("serialNumber", UNSET)

        certificate_pem = d.pop("certificatePem", UNSET)

        chain_pem = d.pop("chainPem", UNSET)

        _not_before = d.pop("notBefore", UNSET)
        not_before: datetime.datetime | Unset
        if isinstance(_not_before, Unset):
            not_before = UNSET
        else:
            not_before = isoparse(_not_before)

        _not_after = d.pop("notAfter", UNSET)
        not_after: datetime.datetime | Unset
        if isinstance(_not_after, Unset):
            not_after = UNSET
        else:
            not_after = isoparse(_not_after)

        post_external_sign_response_200 = cls(
            idempotent=idempotent,
            id=id,
            serial_number=serial_number,
            certificate_pem=certificate_pem,
            chain_pem=chain_pem,
            not_before=not_before,
            not_after=not_after,
        )

        post_external_sign_response_200.additional_properties = d
        return post_external_sign_response_200

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
