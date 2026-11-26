from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_external_health_response_200_cluster import (
        GetExternalHealthResponse200Cluster,
    )
    from ..models.get_external_health_response_200_integration import (
        GetExternalHealthResponse200Integration,
    )


T = TypeVar("T", bound="GetExternalHealthResponse200")


@_attrs_define
class GetExternalHealthResponse200:
    """
    Attributes:
        status (str | Unset):
        integration (GetExternalHealthResponse200Integration | Unset):
        cluster (GetExternalHealthResponse200Cluster | Unset): Compatibility identity for older cert-manager clients;
            use integration.
        timestamp (datetime.datetime | Unset):
    """

    status: str | Unset = UNSET
    integration: GetExternalHealthResponse200Integration | Unset = UNSET
    cluster: GetExternalHealthResponse200Cluster | Unset = UNSET
    timestamp: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status

        integration: dict[str, Any] | Unset = UNSET
        if not isinstance(self.integration, Unset):
            integration = self.integration.to_dict()

        cluster: dict[str, Any] | Unset = UNSET
        if not isinstance(self.cluster, Unset):
            cluster = self.cluster.to_dict()

        timestamp: str | Unset = UNSET
        if not isinstance(self.timestamp, Unset):
            timestamp = self.timestamp.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if status is not UNSET:
            field_dict["status"] = status
        if integration is not UNSET:
            field_dict["integration"] = integration
        if cluster is not UNSET:
            field_dict["cluster"] = cluster
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_external_health_response_200_cluster import (
            GetExternalHealthResponse200Cluster,
        )
        from ..models.get_external_health_response_200_integration import (
            GetExternalHealthResponse200Integration,
        )

        d = dict(src_dict)
        status = d.pop("status", UNSET)

        _integration = d.pop("integration", UNSET)
        integration: GetExternalHealthResponse200Integration | Unset
        if isinstance(_integration, Unset):
            integration = UNSET
        else:
            integration = GetExternalHealthResponse200Integration.from_dict(
                _integration
            )

        _cluster = d.pop("cluster", UNSET)
        cluster: GetExternalHealthResponse200Cluster | Unset
        if isinstance(_cluster, Unset):
            cluster = UNSET
        else:
            cluster = GetExternalHealthResponse200Cluster.from_dict(_cluster)

        _timestamp = d.pop("timestamp", UNSET)
        timestamp: datetime.datetime | Unset
        if isinstance(_timestamp, Unset):
            timestamp = UNSET
        else:
            timestamp = isoparse(_timestamp)

        get_external_health_response_200 = cls(
            status=status,
            integration=integration,
            cluster=cluster,
            timestamp=timestamp,
        )

        get_external_health_response_200.additional_properties = d
        return get_external_health_response_200

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
