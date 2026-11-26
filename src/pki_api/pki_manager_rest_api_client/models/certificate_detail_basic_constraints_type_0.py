from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CertificateDetailBasicConstraintsType0")


@_attrs_define
class CertificateDetailBasicConstraintsType0:
    """
    Attributes:
        c_a (bool):
        path_len_constraint (float | None):
    """

    c_a: bool
    path_len_constraint: float | None
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        c_a = self.c_a

        path_len_constraint: float | None
        path_len_constraint = self.path_len_constraint

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cA": c_a,
                "pathLenConstraint": path_len_constraint,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        c_a = d.pop("cA")

        def _parse_path_len_constraint(data: object) -> float | None:
            if data is None:
                return data
            return cast(float | None, data)

        path_len_constraint = _parse_path_len_constraint(d.pop("pathLenConstraint"))

        certificate_detail_basic_constraints_type_0 = cls(
            c_a=c_a,
            path_len_constraint=path_len_constraint,
        )

        certificate_detail_basic_constraints_type_0.additional_properties = d
        return certificate_detail_basic_constraints_type_0

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
