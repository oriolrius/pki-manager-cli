from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="PostExternalRaProvisionBody")


@_attrs_define
class PostExternalRaProvisionBody:
    """ """

    def to_dict(self) -> dict[str, Any]:

        field_dict: dict[str, Any] = {}

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        post_external_ra_provision_body = cls()

        return post_external_ra_provision_body
