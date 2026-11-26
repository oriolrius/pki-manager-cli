from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="PostSshPrincipalsRevokeGrantBody")


@_attrs_define
class PostSshPrincipalsRevokeGrantBody:
    """
    Attributes:
        identity_id (str):
        principal_id (str):
    """

    identity_id: str
    principal_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        identity_id = self.identity_id

        principal_id = self.principal_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "identityId": identity_id,
                "principalId": principal_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        identity_id = d.pop("identityId")

        principal_id = d.pop("principalId")

        post_ssh_principals_revoke_grant_body = cls(
            identity_id=identity_id,
            principal_id=principal_id,
        )

        post_ssh_principals_revoke_grant_body.additional_properties = d
        return post_ssh_principals_revoke_grant_body

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
