from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostSshHostsIssueBody")


@_attrs_define
class PostSshHostsIssueBody:
    """
    Attributes:
        host_id (str):
        ca_id (str | Unset):
        valid_for_seconds (int | Unset):
        key_id (str | Unset):
        serial (str | Unset):
    """

    host_id: str
    ca_id: str | Unset = UNSET
    valid_for_seconds: int | Unset = UNSET
    key_id: str | Unset = UNSET
    serial: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        host_id = self.host_id

        ca_id = self.ca_id

        valid_for_seconds = self.valid_for_seconds

        key_id = self.key_id

        serial = self.serial

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "hostId": host_id,
            }
        )
        if ca_id is not UNSET:
            field_dict["caId"] = ca_id
        if valid_for_seconds is not UNSET:
            field_dict["validForSeconds"] = valid_for_seconds
        if key_id is not UNSET:
            field_dict["keyId"] = key_id
        if serial is not UNSET:
            field_dict["serial"] = serial

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        host_id = d.pop("hostId")

        ca_id = d.pop("caId", UNSET)

        valid_for_seconds = d.pop("validForSeconds", UNSET)

        key_id = d.pop("keyId", UNSET)

        serial = d.pop("serial", UNSET)

        post_ssh_hosts_issue_body = cls(
            host_id=host_id,
            ca_id=ca_id,
            valid_for_seconds=valid_for_seconds,
            key_id=key_id,
            serial=serial,
        )

        post_ssh_hosts_issue_body.additional_properties = d
        return post_ssh_hosts_issue_body

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
