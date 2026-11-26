from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BulkDeleteCertificatesRequest")


@_attrs_define
class BulkDeleteCertificatesRequest:
    """
    Attributes:
        certificate_ids (list[str]):
        destroy_key (bool | Unset):  Default: True.
        remove_from_crl (bool | Unset):  Default: False.
    """

    certificate_ids: list[str]
    destroy_key: bool | Unset = True
    remove_from_crl: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        certificate_ids = self.certificate_ids

        destroy_key = self.destroy_key

        remove_from_crl = self.remove_from_crl

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "certificateIds": certificate_ids,
            }
        )
        if destroy_key is not UNSET:
            field_dict["destroyKey"] = destroy_key
        if remove_from_crl is not UNSET:
            field_dict["removeFromCrl"] = remove_from_crl

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        certificate_ids = cast(list[str], d.pop("certificateIds"))

        destroy_key = d.pop("destroyKey", UNSET)

        remove_from_crl = d.pop("removeFromCrl", UNSET)

        bulk_delete_certificates_request = cls(
            certificate_ids=certificate_ids,
            destroy_key=destroy_key,
            remove_from_crl=remove_from_crl,
        )

        bulk_delete_certificates_request.additional_properties = d
        return bulk_delete_certificates_request

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
