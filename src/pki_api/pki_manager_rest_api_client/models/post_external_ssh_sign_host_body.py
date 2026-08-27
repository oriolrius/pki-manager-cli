from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostExternalSshSignHostBody")


@_attrs_define
class PostExternalSshSignHostBody:
    """
    Attributes:
        fqdn (str):
        openssh_host_pubkey (str):
        addresses (list[str] | Unset):
        valid_for_seconds (int | Unset):
        key_id (str | Unset):
    """

    fqdn: str
    openssh_host_pubkey: str
    addresses: list[str] | Unset = UNSET
    valid_for_seconds: int | Unset = UNSET
    key_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        fqdn = self.fqdn

        openssh_host_pubkey = self.openssh_host_pubkey

        addresses: list[str] | Unset = UNSET
        if not isinstance(self.addresses, Unset):
            addresses = self.addresses

        valid_for_seconds = self.valid_for_seconds

        key_id = self.key_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fqdn": fqdn,
                "opensshHostPubkey": openssh_host_pubkey,
            }
        )
        if addresses is not UNSET:
            field_dict["addresses"] = addresses
        if valid_for_seconds is not UNSET:
            field_dict["validForSeconds"] = valid_for_seconds
        if key_id is not UNSET:
            field_dict["keyId"] = key_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        fqdn = d.pop("fqdn")

        openssh_host_pubkey = d.pop("opensshHostPubkey")

        addresses = cast(list[str], d.pop("addresses", UNSET))

        valid_for_seconds = d.pop("validForSeconds", UNSET)

        key_id = d.pop("keyId", UNSET)

        post_external_ssh_sign_host_body = cls(
            fqdn=fqdn,
            openssh_host_pubkey=openssh_host_pubkey,
            addresses=addresses,
            valid_for_seconds=valid_for_seconds,
            key_id=key_id,
        )

        post_external_ssh_sign_host_body.additional_properties = d
        return post_external_ssh_sign_host_body

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
