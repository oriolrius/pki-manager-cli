from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostExternalSshRegisterHostPubkeyBody")


@_attrs_define
class PostExternalSshRegisterHostPubkeyBody:
    """
    Attributes:
        fqdn (str | Unset): Host FQDN (alias: host_id)
        host_id (str | Unset): Host FQDN (alias of fqdn)
    """

    fqdn: str | Unset = UNSET
    host_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        fqdn = self.fqdn

        host_id = self.host_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if fqdn is not UNSET:
            field_dict["fqdn"] = fqdn
        if host_id is not UNSET:
            field_dict["host_id"] = host_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        fqdn = d.pop("fqdn", UNSET)

        host_id = d.pop("host_id", UNSET)

        post_external_ssh_register_host_pubkey_body = cls(
            fqdn=fqdn,
            host_id=host_id,
        )

        post_external_ssh_register_host_pubkey_body.additional_properties = d
        return post_external_ssh_register_host_pubkey_body

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
