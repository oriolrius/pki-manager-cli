from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.post_ssh_zones_ref_unarchive_response_400_error import (
        PostSshZonesRefUnarchiveResponse400Error,
    )


T = TypeVar("T", bound="PostSshZonesRefUnarchiveResponse400")


@_attrs_define
class PostSshZonesRefUnarchiveResponse400:
    """
    Attributes:
        error (PostSshZonesRefUnarchiveResponse400Error):
    """

    error: PostSshZonesRefUnarchiveResponse400Error
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        error = self.error.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "error": error,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_ssh_zones_ref_unarchive_response_400_error import (
            PostSshZonesRefUnarchiveResponse400Error,
        )

        d = dict(src_dict)
        error = PostSshZonesRefUnarchiveResponse400Error.from_dict(d.pop("error"))

        post_ssh_zones_ref_unarchive_response_400 = cls(
            error=error,
        )

        post_ssh_zones_ref_unarchive_response_400.additional_properties = d
        return post_ssh_zones_ref_unarchive_response_400

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
