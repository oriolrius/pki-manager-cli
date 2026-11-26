from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetCrlRequest")


@_attrs_define
class GetCrlRequest:
    """
    Attributes:
        ca_id (str):
        crl_number (int | Unset):
    """

    ca_id: str
    crl_number: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ca_id = self.ca_id

        crl_number = self.crl_number

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "caId": ca_id,
            }
        )
        if crl_number is not UNSET:
            field_dict["crlNumber"] = crl_number

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ca_id = d.pop("caId")

        crl_number = d.pop("crlNumber", UNSET)

        get_crl_request = cls(
            ca_id=ca_id,
            crl_number=crl_number,
        )

        get_crl_request.additional_properties = d
        return get_crl_request

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
