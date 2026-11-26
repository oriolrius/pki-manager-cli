from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ListCrlsRequest")


@_attrs_define
class ListCrlsRequest:
    """
    Attributes:
        ca_id (str):
        limit (int | Unset):  Default: 50.
        offset (int | Unset):  Default: 0.
    """

    ca_id: str
    limit: int | Unset = 50
    offset: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ca_id = self.ca_id

        limit = self.limit

        offset = self.offset

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "caId": ca_id,
            }
        )
        if limit is not UNSET:
            field_dict["limit"] = limit
        if offset is not UNSET:
            field_dict["offset"] = offset

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ca_id = d.pop("caId")

        limit = d.pop("limit", UNSET)

        offset = d.pop("offset", UNSET)

        list_crls_request = cls(
            ca_id=ca_id,
            limit=limit,
            offset=offset,
        )

        list_crls_request.additional_properties = d
        return list_crls_request

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
