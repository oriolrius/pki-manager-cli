from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.post_external_revoke_response_200_status import (
    PostExternalRevokeResponse200Status,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="PostExternalRevokeResponse200")


@_attrs_define
class PostExternalRevokeResponse200:
    """
    Attributes:
        id (str | Unset):
        serial_number (str | Unset):
        status (PostExternalRevokeResponse200Status | Unset):
        revocation_date (datetime.datetime | Unset):
        idempotent (bool | Unset): Present and true when the certificate was already revoked.
    """

    id: str | Unset = UNSET
    serial_number: str | Unset = UNSET
    status: PostExternalRevokeResponse200Status | Unset = UNSET
    revocation_date: datetime.datetime | Unset = UNSET
    idempotent: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        serial_number = self.serial_number

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        revocation_date: str | Unset = UNSET
        if not isinstance(self.revocation_date, Unset):
            revocation_date = self.revocation_date.isoformat()

        idempotent = self.idempotent

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if serial_number is not UNSET:
            field_dict["serialNumber"] = serial_number
        if status is not UNSET:
            field_dict["status"] = status
        if revocation_date is not UNSET:
            field_dict["revocationDate"] = revocation_date
        if idempotent is not UNSET:
            field_dict["idempotent"] = idempotent

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        serial_number = d.pop("serialNumber", UNSET)

        _status = d.pop("status", UNSET)
        status: PostExternalRevokeResponse200Status | Unset
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = PostExternalRevokeResponse200Status(_status)

        _revocation_date = d.pop("revocationDate", UNSET)
        revocation_date: datetime.datetime | Unset
        if isinstance(_revocation_date, Unset):
            revocation_date = UNSET
        else:
            revocation_date = isoparse(_revocation_date)

        idempotent = d.pop("idempotent", UNSET)

        post_external_revoke_response_200 = cls(
            id=id,
            serial_number=serial_number,
            status=status,
            revocation_date=revocation_date,
            idempotent=idempotent,
        )

        post_external_revoke_response_200.additional_properties = d
        return post_external_revoke_response_200

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
