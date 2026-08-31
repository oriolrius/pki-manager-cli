from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.post_ssh_cas_import_body_ca_type import PostSshCasImportBodyCaType
from ..types import UNSET, Unset

T = TypeVar("T", bound="PostSshCasImportBody")


@_attrs_define
class PostSshCasImportBody:
    """
    Attributes:
        ca_type (PostSshCasImportBodyCaType):
        kms_key_id (str):
        kms_public_key_id (str):
        label (str | Unset):
    """

    ca_type: PostSshCasImportBodyCaType
    kms_key_id: str
    kms_public_key_id: str
    label: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ca_type = self.ca_type.value

        kms_key_id = self.kms_key_id

        kms_public_key_id = self.kms_public_key_id

        label = self.label

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "caType": ca_type,
                "kmsKeyId": kms_key_id,
                "kmsPublicKeyId": kms_public_key_id,
            }
        )
        if label is not UNSET:
            field_dict["label"] = label

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ca_type = PostSshCasImportBodyCaType(d.pop("caType"))

        kms_key_id = d.pop("kmsKeyId")

        kms_public_key_id = d.pop("kmsPublicKeyId")

        label = d.pop("label", UNSET)

        post_ssh_cas_import_body = cls(
            ca_type=ca_type,
            kms_key_id=kms_key_id,
            kms_public_key_id=kms_public_key_id,
            label=label,
        )

        post_ssh_cas_import_body.additional_properties = d
        return post_ssh_cas_import_body

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
