from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.post_ssh_users_issue_body_extensions_item import (
    PostSshUsersIssueBodyExtensionsItem,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="PostSshUsersIssueBody")


@_attrs_define
class PostSshUsersIssueBody:
    """
    Attributes:
        identity_id (str):
        ssh_public_key (str):
        principals (list[str]):
        ca_id (str | Unset):
        extensions (list[PostSshUsersIssueBodyExtensionsItem] | Unset):
        force_command (str | Unset):
        source_address (str | Unset):
        valid_for_seconds (int | Unset):
        key_id (str | Unset):
        enforce_entitlement (bool | Unset):
    """

    identity_id: str
    ssh_public_key: str
    principals: list[str]
    ca_id: str | Unset = UNSET
    extensions: list[PostSshUsersIssueBodyExtensionsItem] | Unset = UNSET
    force_command: str | Unset = UNSET
    source_address: str | Unset = UNSET
    valid_for_seconds: int | Unset = UNSET
    key_id: str | Unset = UNSET
    enforce_entitlement: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        identity_id = self.identity_id

        ssh_public_key = self.ssh_public_key

        principals = self.principals

        ca_id = self.ca_id

        extensions: list[str] | Unset = UNSET
        if not isinstance(self.extensions, Unset):
            extensions = []
            for extensions_item_data in self.extensions:
                extensions_item = extensions_item_data.value
                extensions.append(extensions_item)

        force_command = self.force_command

        source_address = self.source_address

        valid_for_seconds = self.valid_for_seconds

        key_id = self.key_id

        enforce_entitlement = self.enforce_entitlement

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "identityId": identity_id,
                "sshPublicKey": ssh_public_key,
                "principals": principals,
            }
        )
        if ca_id is not UNSET:
            field_dict["caId"] = ca_id
        if extensions is not UNSET:
            field_dict["extensions"] = extensions
        if force_command is not UNSET:
            field_dict["forceCommand"] = force_command
        if source_address is not UNSET:
            field_dict["sourceAddress"] = source_address
        if valid_for_seconds is not UNSET:
            field_dict["validForSeconds"] = valid_for_seconds
        if key_id is not UNSET:
            field_dict["keyId"] = key_id
        if enforce_entitlement is not UNSET:
            field_dict["enforceEntitlement"] = enforce_entitlement

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        identity_id = d.pop("identityId")

        ssh_public_key = d.pop("sshPublicKey")

        principals = cast(list[str], d.pop("principals"))

        ca_id = d.pop("caId", UNSET)

        _extensions = d.pop("extensions", UNSET)
        extensions: list[PostSshUsersIssueBodyExtensionsItem] | Unset = UNSET
        if _extensions is not UNSET:
            extensions = []
            for extensions_item_data in _extensions:
                extensions_item = PostSshUsersIssueBodyExtensionsItem(
                    extensions_item_data
                )

                extensions.append(extensions_item)

        force_command = d.pop("forceCommand", UNSET)

        source_address = d.pop("sourceAddress", UNSET)

        valid_for_seconds = d.pop("validForSeconds", UNSET)

        key_id = d.pop("keyId", UNSET)

        enforce_entitlement = d.pop("enforceEntitlement", UNSET)

        post_ssh_users_issue_body = cls(
            identity_id=identity_id,
            ssh_public_key=ssh_public_key,
            principals=principals,
            ca_id=ca_id,
            extensions=extensions,
            force_command=force_command,
            source_address=source_address,
            valid_for_seconds=valid_for_seconds,
            key_id=key_id,
            enforce_entitlement=enforce_entitlement,
        )

        post_ssh_users_issue_body.additional_properties = d
        return post_ssh_users_issue_body

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
