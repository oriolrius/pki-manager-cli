from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostSshIdentitiesBody")


@_attrs_define
class PostSshIdentitiesBody:
    """
    Attributes:
        subject (str):
        email (str | Unset):
        external_subject (str | Unset):
        zone (str | Unset):
    """

    subject: str
    email: str | Unset = UNSET
    external_subject: str | Unset = UNSET
    zone: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        subject = self.subject

        email = self.email

        external_subject = self.external_subject

        zone = self.zone

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "subject": subject,
            }
        )
        if email is not UNSET:
            field_dict["email"] = email
        if external_subject is not UNSET:
            field_dict["externalSubject"] = external_subject
        if zone is not UNSET:
            field_dict["zone"] = zone

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        subject = d.pop("subject")

        email = d.pop("email", UNSET)

        external_subject = d.pop("externalSubject", UNSET)

        zone = d.pop("zone", UNSET)

        post_ssh_identities_body = cls(
            subject=subject,
            email=email,
            external_subject=external_subject,
            zone=zone,
        )

        post_ssh_identities_body.additional_properties = d
        return post_ssh_identities_body

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
