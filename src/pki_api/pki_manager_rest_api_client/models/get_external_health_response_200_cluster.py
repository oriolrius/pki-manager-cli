from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetExternalHealthResponse200Cluster")


@_attrs_define
class GetExternalHealthResponse200Cluster:
    """Compatibility identity for older cert-manager clients; use integration.

    Attributes:
        id (str | Unset):
        name (str | Unset):
        ca_id (str | Unset):
    """

    id: str | Unset = UNSET
    name: str | Unset = UNSET
    ca_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        ca_id = self.ca_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if ca_id is not UNSET:
            field_dict["caId"] = ca_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        ca_id = d.pop("caId", UNSET)

        get_external_health_response_200_cluster = cls(
            id=id,
            name=name,
            ca_id=ca_id,
        )

        get_external_health_response_200_cluster.additional_properties = d
        return get_external_health_response_200_cluster

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
