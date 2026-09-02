from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.post_ssh_cas_body_ca_type import PostSshCasBodyCaType
from ..types import UNSET, Unset

T = TypeVar("T", bound="PostSshCasBody")


@_attrs_define
class PostSshCasBody:
    """
    Attributes:
        ca_type (PostSshCasBodyCaType):
        label (str | Unset):
        zone (str | Unset):
    """

    ca_type: PostSshCasBodyCaType
    label: str | Unset = UNSET
    zone: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ca_type = self.ca_type.value

        label = self.label

        zone = self.zone

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "caType": ca_type,
            }
        )
        if label is not UNSET:
            field_dict["label"] = label
        if zone is not UNSET:
            field_dict["zone"] = zone

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ca_type = PostSshCasBodyCaType(d.pop("caType"))

        label = d.pop("label", UNSET)

        zone = d.pop("zone", UNSET)

        post_ssh_cas_body = cls(
            ca_type=ca_type,
            label=label,
            zone=zone,
        )

        post_ssh_cas_body.additional_properties = d
        return post_ssh_cas_body

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
