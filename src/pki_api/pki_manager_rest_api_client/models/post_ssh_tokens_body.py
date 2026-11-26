from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.post_ssh_tokens_body_op_set_item import PostSshTokensBodyOpSetItem
from ..types import UNSET, Unset

T = TypeVar("T", bound="PostSshTokensBody")


@_attrs_define
class PostSshTokensBody:
    """
    Attributes:
        name (str):
        op_set (list[PostSshTokensBodyOpSetItem]):
        user_ca_id (str | Unset):
        host_ca_id (str | Unset):
        zone (str | Unset):
        allowed_principals (list[str] | Unset):
        max_valid_for_seconds (int | Unset):
    """

    name: str
    op_set: list[PostSshTokensBodyOpSetItem]
    user_ca_id: str | Unset = UNSET
    host_ca_id: str | Unset = UNSET
    zone: str | Unset = UNSET
    allowed_principals: list[str] | Unset = UNSET
    max_valid_for_seconds: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        op_set = []
        for op_set_item_data in self.op_set:
            op_set_item = op_set_item_data.value
            op_set.append(op_set_item)

        user_ca_id = self.user_ca_id

        host_ca_id = self.host_ca_id

        zone = self.zone

        allowed_principals: list[str] | Unset = UNSET
        if not isinstance(self.allowed_principals, Unset):
            allowed_principals = self.allowed_principals

        max_valid_for_seconds = self.max_valid_for_seconds

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "opSet": op_set,
            }
        )
        if user_ca_id is not UNSET:
            field_dict["userCaId"] = user_ca_id
        if host_ca_id is not UNSET:
            field_dict["hostCaId"] = host_ca_id
        if zone is not UNSET:
            field_dict["zone"] = zone
        if allowed_principals is not UNSET:
            field_dict["allowedPrincipals"] = allowed_principals
        if max_valid_for_seconds is not UNSET:
            field_dict["maxValidForSeconds"] = max_valid_for_seconds

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        op_set = []
        _op_set = d.pop("opSet")
        for op_set_item_data in _op_set:
            op_set_item = PostSshTokensBodyOpSetItem(op_set_item_data)

            op_set.append(op_set_item)

        user_ca_id = d.pop("userCaId", UNSET)

        host_ca_id = d.pop("hostCaId", UNSET)

        zone = d.pop("zone", UNSET)

        allowed_principals = cast(list[str], d.pop("allowedPrincipals", UNSET))

        max_valid_for_seconds = d.pop("maxValidForSeconds", UNSET)

        post_ssh_tokens_body = cls(
            name=name,
            op_set=op_set,
            user_ca_id=user_ca_id,
            host_ca_id=host_ca_id,
            zone=zone,
            allowed_principals=allowed_principals,
            max_valid_for_seconds=max_valid_for_seconds,
        )

        post_ssh_tokens_body.additional_properties = d
        return post_ssh_tokens_body

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
