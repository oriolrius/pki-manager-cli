from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostExternalSshSignUserBody")


@_attrs_define
class PostExternalSshSignUserBody:
    """
    Attributes:
        subject (str):
        ssh_public_key (str):
        principals (list[str]):
        extensions (list[str] | Unset):
        force_command (str | Unset):
        source_address (str | Unset):
        valid_for_seconds (int | Unset):
        key_id (str | Unset):
    """

    subject: str
    ssh_public_key: str
    principals: list[str]
    extensions: list[str] | Unset = UNSET
    force_command: str | Unset = UNSET
    source_address: str | Unset = UNSET
    valid_for_seconds: int | Unset = UNSET
    key_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        subject = self.subject

        ssh_public_key = self.ssh_public_key

        principals = self.principals

        extensions: list[str] | Unset = UNSET
        if not isinstance(self.extensions, Unset):
            extensions = self.extensions

        force_command = self.force_command

        source_address = self.source_address

        valid_for_seconds = self.valid_for_seconds

        key_id = self.key_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "subject": subject,
                "sshPublicKey": ssh_public_key,
                "principals": principals,
            }
        )
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

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        subject = d.pop("subject")

        ssh_public_key = d.pop("sshPublicKey")

        principals = cast(list[str], d.pop("principals"))

        extensions = cast(list[str], d.pop("extensions", UNSET))

        force_command = d.pop("forceCommand", UNSET)

        source_address = d.pop("sourceAddress", UNSET)

        valid_for_seconds = d.pop("validForSeconds", UNSET)

        key_id = d.pop("keyId", UNSET)

        post_external_ssh_sign_user_body = cls(
            subject=subject,
            ssh_public_key=ssh_public_key,
            principals=principals,
            extensions=extensions,
            force_command=force_command,
            source_address=source_address,
            valid_for_seconds=valid_for_seconds,
            key_id=key_id,
        )

        post_external_ssh_sign_user_body.additional_properties = d
        return post_external_ssh_sign_user_body

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
