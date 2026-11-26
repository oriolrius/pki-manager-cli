from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DeleteCertificateRequest")


@_attrs_define
class DeleteCertificateRequest:
    """
    Attributes:
        id (str):
        destroy_key (bool | Unset):  Default: True.
        remove_from_crl (bool | Unset):  Default: False.
        force_delete (bool | Unset):  Default: False.
    """

    id: str
    destroy_key: bool | Unset = True
    remove_from_crl: bool | Unset = False
    force_delete: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        destroy_key = self.destroy_key

        remove_from_crl = self.remove_from_crl

        force_delete = self.force_delete

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
            }
        )
        if destroy_key is not UNSET:
            field_dict["destroyKey"] = destroy_key
        if remove_from_crl is not UNSET:
            field_dict["removeFromCrl"] = remove_from_crl
        if force_delete is not UNSET:
            field_dict["forceDelete"] = force_delete

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        destroy_key = d.pop("destroyKey", UNSET)

        remove_from_crl = d.pop("removeFromCrl", UNSET)

        force_delete = d.pop("forceDelete", UNSET)

        delete_certificate_request = cls(
            id=id,
            destroy_key=destroy_key,
            remove_from_crl=remove_from_crl,
            force_delete=force_delete,
        )

        delete_certificate_request.additional_properties = d
        return delete_certificate_request

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
