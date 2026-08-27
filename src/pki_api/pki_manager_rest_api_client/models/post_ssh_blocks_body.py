from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostSshBlocksBody")


@_attrs_define
class PostSshBlocksBody:
    """
    Attributes:
        host_id (str):
        identity_id (str):
        reason (str | Unset):
    """

    host_id: str
    identity_id: str
    reason: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        host_id = self.host_id

        identity_id = self.identity_id

        reason = self.reason

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "hostId": host_id,
                "identityId": identity_id,
            }
        )
        if reason is not UNSET:
            field_dict["reason"] = reason

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        host_id = d.pop("hostId")

        identity_id = d.pop("identityId")

        reason = d.pop("reason", UNSET)

        post_ssh_blocks_body = cls(
            host_id=host_id,
            identity_id=identity_id,
            reason=reason,
        )

        post_ssh_blocks_body.additional_properties = d
        return post_ssh_blocks_body

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
