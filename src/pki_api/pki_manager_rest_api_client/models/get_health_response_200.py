from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.get_health_response_200_status import GetHealthResponse200Status

T = TypeVar("T", bound="GetHealthResponse200")


@_attrs_define
class GetHealthResponse200:
    """
    Attributes:
        status (GetHealthResponse200Status): API health status
        version (str): API version
        timestamp (datetime.datetime): Current server timestamp
    """

    status: GetHealthResponse200Status
    version: str
    timestamp: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status.value

        version = self.version

        timestamp = self.timestamp.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
                "version": version,
                "timestamp": timestamp,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        status = GetHealthResponse200Status(d.pop("status"))

        version = d.pop("version")

        timestamp = isoparse(d.pop("timestamp"))

        get_health_response_200 = cls(
            status=status,
            version=version,
            timestamp=timestamp,
        )

        get_health_response_200.additional_properties = d
        return get_health_response_200

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
