from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.generate_report_request_format import GenerateReportRequestFormat
from ..models.generate_report_request_report_type import GenerateReportRequestReportType
from ..types import UNSET, Unset

T = TypeVar("T", bound="GenerateReportRequest")


@_attrs_define
class GenerateReportRequest:
    """
    Attributes:
        report_type (GenerateReportRequestReportType):
        format_ (GenerateReportRequestFormat | Unset):  Default: GenerateReportRequestFormat.CSV.
        ca_id (str | Unset):
        start_date (int | Unset):
        end_date (int | Unset):
    """

    report_type: GenerateReportRequestReportType
    format_: GenerateReportRequestFormat | Unset = GenerateReportRequestFormat.CSV
    ca_id: str | Unset = UNSET
    start_date: int | Unset = UNSET
    end_date: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        report_type = self.report_type.value

        format_: str | Unset = UNSET
        if not isinstance(self.format_, Unset):
            format_ = self.format_.value

        ca_id = self.ca_id

        start_date = self.start_date

        end_date = self.end_date

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "reportType": report_type,
            }
        )
        if format_ is not UNSET:
            field_dict["format"] = format_
        if ca_id is not UNSET:
            field_dict["caId"] = ca_id
        if start_date is not UNSET:
            field_dict["startDate"] = start_date
        if end_date is not UNSET:
            field_dict["endDate"] = end_date

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        report_type = GenerateReportRequestReportType(d.pop("reportType"))

        _format_ = d.pop("format", UNSET)
        format_: GenerateReportRequestFormat | Unset
        if isinstance(_format_, Unset):
            format_ = UNSET
        else:
            format_ = GenerateReportRequestFormat(_format_)

        ca_id = d.pop("caId", UNSET)

        start_date = d.pop("startDate", UNSET)

        end_date = d.pop("endDate", UNSET)

        generate_report_request = cls(
            report_type=report_type,
            format_=format_,
            ca_id=ca_id,
            start_date=start_date,
            end_date=end_date,
        )

        generate_report_request.additional_properties = d
        return generate_report_request

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
