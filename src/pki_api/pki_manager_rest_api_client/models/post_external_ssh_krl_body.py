from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostExternalSshKrlBody")


@_attrs_define
class PostExternalSshKrlBody:
    """
    Attributes:
        host_id (str | Unset): Target host FQDN
        zone (str | Unset): Zone id or slug — required only when the FQDN exists in more than one zone (decision-017 A2)
    """

    host_id: str | Unset = UNSET
    zone: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        host_id = self.host_id

        zone = self.zone

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if host_id is not UNSET:
            field_dict["host_id"] = host_id
        if zone is not UNSET:
            field_dict["zone"] = zone

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        host_id = d.pop("host_id", UNSET)

        zone = d.pop("zone", UNSET)

        post_external_ssh_krl_body = cls(
            host_id=host_id,
            zone=zone,
        )

        post_external_ssh_krl_body.additional_properties = d
        return post_external_ssh_krl_body

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
