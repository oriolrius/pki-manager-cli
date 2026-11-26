from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.list_cas_request_algorithm import ListCasRequestAlgorithm
from ..models.list_cas_request_sort_by import ListCasRequestSortBy
from ..models.list_cas_request_sort_order import ListCasRequestSortOrder
from ..models.list_cas_request_status import ListCasRequestStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="ListCasRequest")


@_attrs_define
class ListCasRequest:
    """
    Attributes:
        status (ListCasRequestStatus | Unset):
        algorithm (ListCasRequestAlgorithm | Unset):
        search (str | Unset):
        sort_by (ListCasRequestSortBy | Unset):  Default: ListCasRequestSortBy.ISSUEDDATE.
        sort_order (ListCasRequestSortOrder | Unset):  Default: ListCasRequestSortOrder.DESC.
        limit (int | Unset):  Default: 50.
        offset (int | Unset):  Default: 0.
    """

    status: ListCasRequestStatus | Unset = UNSET
    algorithm: ListCasRequestAlgorithm | Unset = UNSET
    search: str | Unset = UNSET
    sort_by: ListCasRequestSortBy | Unset = ListCasRequestSortBy.ISSUEDDATE
    sort_order: ListCasRequestSortOrder | Unset = ListCasRequestSortOrder.DESC
    limit: int | Unset = 50
    offset: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        algorithm: str | Unset = UNSET
        if not isinstance(self.algorithm, Unset):
            algorithm = self.algorithm.value

        search = self.search

        sort_by: str | Unset = UNSET
        if not isinstance(self.sort_by, Unset):
            sort_by = self.sort_by.value

        sort_order: str | Unset = UNSET
        if not isinstance(self.sort_order, Unset):
            sort_order = self.sort_order.value

        limit = self.limit

        offset = self.offset

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if status is not UNSET:
            field_dict["status"] = status
        if algorithm is not UNSET:
            field_dict["algorithm"] = algorithm
        if search is not UNSET:
            field_dict["search"] = search
        if sort_by is not UNSET:
            field_dict["sortBy"] = sort_by
        if sort_order is not UNSET:
            field_dict["sortOrder"] = sort_order
        if limit is not UNSET:
            field_dict["limit"] = limit
        if offset is not UNSET:
            field_dict["offset"] = offset

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _status = d.pop("status", UNSET)
        status: ListCasRequestStatus | Unset
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = ListCasRequestStatus(_status)

        _algorithm = d.pop("algorithm", UNSET)
        algorithm: ListCasRequestAlgorithm | Unset
        if isinstance(_algorithm, Unset):
            algorithm = UNSET
        else:
            algorithm = ListCasRequestAlgorithm(_algorithm)

        search = d.pop("search", UNSET)

        _sort_by = d.pop("sortBy", UNSET)
        sort_by: ListCasRequestSortBy | Unset
        if isinstance(_sort_by, Unset):
            sort_by = UNSET
        else:
            sort_by = ListCasRequestSortBy(_sort_by)

        _sort_order = d.pop("sortOrder", UNSET)
        sort_order: ListCasRequestSortOrder | Unset
        if isinstance(_sort_order, Unset):
            sort_order = UNSET
        else:
            sort_order = ListCasRequestSortOrder(_sort_order)

        limit = d.pop("limit", UNSET)

        offset = d.pop("offset", UNSET)

        list_cas_request = cls(
            status=status,
            algorithm=algorithm,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset,
        )

        list_cas_request.additional_properties = d
        return list_cas_request

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
