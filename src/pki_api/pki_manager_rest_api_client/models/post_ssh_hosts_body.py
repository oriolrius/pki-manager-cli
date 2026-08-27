from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostSshHostsBody")


@_attrs_define
class PostSshHostsBody:
    """
    Attributes:
        fqdn (str):
        openssh_host_pubkey (str):
        display_name (str | Unset):
        addresses (list[str] | Unset):
    """

    fqdn: str
    openssh_host_pubkey: str
    display_name: str | Unset = UNSET
    addresses: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        fqdn = self.fqdn

        openssh_host_pubkey = self.openssh_host_pubkey

        display_name = self.display_name

        addresses: list[str] | Unset = UNSET
        if not isinstance(self.addresses, Unset):
            addresses = self.addresses

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fqdn": fqdn,
                "opensshHostPubkey": openssh_host_pubkey,
            }
        )
        if display_name is not UNSET:
            field_dict["displayName"] = display_name
        if addresses is not UNSET:
            field_dict["addresses"] = addresses

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        fqdn = d.pop("fqdn")

        openssh_host_pubkey = d.pop("opensshHostPubkey")

        display_name = d.pop("displayName", UNSET)

        addresses = cast(list[str], d.pop("addresses", UNSET))

        post_ssh_hosts_body = cls(
            fqdn=fqdn,
            openssh_host_pubkey=openssh_host_pubkey,
            display_name=display_name,
            addresses=addresses,
        )

        post_ssh_hosts_body.additional_properties = d
        return post_ssh_hosts_body

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
