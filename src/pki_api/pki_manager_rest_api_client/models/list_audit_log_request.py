from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.list_audit_log_request_status import ListAuditLogRequestStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="ListAuditLogRequest")


@_attrs_define
class ListAuditLogRequest:
    """
    Attributes:
        operation (str | Unset):
        entity_type (str | Unset):
        entity_id (str | Unset):
        status (ListAuditLogRequestStatus | Unset):
        start_date (int | Unset):
        end_date (int | Unset):
        limit (int | Unset):  Default: 100.
        offset (int | Unset):  Default: 0.
    """

    operation: str | Unset = UNSET
    entity_type: str | Unset = UNSET
    entity_id: str | Unset = UNSET
    status: ListAuditLogRequestStatus | Unset = UNSET
    start_date: int | Unset = UNSET
    end_date: int | Unset = UNSET
    limit: int | Unset = 100
    offset: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        operation = self.operation

        entity_type = self.entity_type

        entity_id = self.entity_id

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        start_date = self.start_date

        end_date = self.end_date

        limit = self.limit

        offset = self.offset

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if operation is not UNSET:
            field_dict["operation"] = operation
        if entity_type is not UNSET:
            field_dict["entityType"] = entity_type
        if entity_id is not UNSET:
            field_dict["entityId"] = entity_id
        if status is not UNSET:
            field_dict["status"] = status
        if start_date is not UNSET:
            field_dict["startDate"] = start_date
        if end_date is not UNSET:
            field_dict["endDate"] = end_date
        if limit is not UNSET:
            field_dict["limit"] = limit
        if offset is not UNSET:
            field_dict["offset"] = offset

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        operation = d.pop("operation", UNSET)

        entity_type = d.pop("entityType", UNSET)

        entity_id = d.pop("entityId", UNSET)

        _status = d.pop("status", UNSET)
        status: ListAuditLogRequestStatus | Unset
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = ListAuditLogRequestStatus(_status)

        start_date = d.pop("startDate", UNSET)

        end_date = d.pop("endDate", UNSET)

        limit = d.pop("limit", UNSET)

        offset = d.pop("offset", UNSET)

        list_audit_log_request = cls(
            operation=operation,
            entity_type=entity_type,
            entity_id=entity_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )

        list_audit_log_request.additional_properties = d
        return list_audit_log_request

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
