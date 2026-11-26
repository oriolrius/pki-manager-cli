from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.get_external_health_response_200_integration_kind import (
    GetExternalHealthResponse200IntegrationKind,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="GetExternalHealthResponse200Integration")


@_attrs_define
class GetExternalHealthResponse200Integration:
    """
    Attributes:
        id (str | Unset):
        name (str | Unset):
        ca_id (str | Unset):
        kind (GetExternalHealthResponse200IntegrationKind | Unset):
    """

    id: str | Unset = UNSET
    name: str | Unset = UNSET
    ca_id: str | Unset = UNSET
    kind: GetExternalHealthResponse200IntegrationKind | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        ca_id = self.ca_id

        kind: str | Unset = UNSET
        if not isinstance(self.kind, Unset):
            kind = self.kind.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if ca_id is not UNSET:
            field_dict["caId"] = ca_id
        if kind is not UNSET:
            field_dict["kind"] = kind

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        ca_id = d.pop("caId", UNSET)

        _kind = d.pop("kind", UNSET)
        kind: GetExternalHealthResponse200IntegrationKind | Unset
        if isinstance(_kind, Unset):
            kind = UNSET
        else:
            kind = GetExternalHealthResponse200IntegrationKind(_kind)

        get_external_health_response_200_integration = cls(
            id=id,
            name=name,
            ca_id=ca_id,
            kind=kind,
        )

        get_external_health_response_200_integration.additional_properties = d
        return get_external_health_response_200_integration

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
