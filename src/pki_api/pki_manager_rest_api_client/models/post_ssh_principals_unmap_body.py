from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="PostSshPrincipalsUnmapBody")


@_attrs_define
class PostSshPrincipalsUnmapBody:
    """
    Attributes:
        host_id (str):
        principal_id (str):
        local_account (str):
    """

    host_id: str
    principal_id: str
    local_account: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        host_id = self.host_id

        principal_id = self.principal_id

        local_account = self.local_account

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "hostId": host_id,
                "principalId": principal_id,
                "localAccount": local_account,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        host_id = d.pop("hostId")

        principal_id = d.pop("principalId")

        local_account = d.pop("localAccount")

        post_ssh_principals_unmap_body = cls(
            host_id=host_id,
            principal_id=principal_id,
            local_account=local_account,
        )

        post_ssh_principals_unmap_body.additional_properties = d
        return post_ssh_principals_unmap_body

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
