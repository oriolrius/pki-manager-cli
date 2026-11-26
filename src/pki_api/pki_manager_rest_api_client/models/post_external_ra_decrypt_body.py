from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="PostExternalRaDecryptBody")


@_attrs_define
class PostExternalRaDecryptBody:
    """
    Attributes:
        data (str):
    """

    data: str

    def to_dict(self) -> dict[str, Any]:
        data = self.data

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "data": data,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        data = d.pop("data")

        post_external_ra_decrypt_body = cls(
            data=data,
        )

        return post_external_ra_decrypt_body
