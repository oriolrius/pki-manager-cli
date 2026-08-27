from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.post_external_sign_body_certificate_type import (
    PostExternalSignBodyCertificateType,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="PostExternalSignBody")


@_attrs_define
class PostExternalSignBody:
    """
    Attributes:
        csr_pem (str): PEM-encoded PKCS#10 CSR to sign
        request_uid (str): Idempotency key; repeat calls for the same uid return the cached certificate
        duration_days (float | Unset): Requested validity in days (clamped server-side to 1..825; default 90)
        certificate_type (PostExternalSignBodyCertificateType | Unset):
        k_8_s_namespace (str | Unset):
        k_8_s_resource (str | Unset):
        san_dns (list[str] | Unset):
        san_ip (list[str] | Unset):
    """

    csr_pem: str
    request_uid: str
    duration_days: float | Unset = UNSET
    certificate_type: PostExternalSignBodyCertificateType | Unset = UNSET
    k_8_s_namespace: str | Unset = UNSET
    k_8_s_resource: str | Unset = UNSET
    san_dns: list[str] | Unset = UNSET
    san_ip: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        csr_pem = self.csr_pem

        request_uid = self.request_uid

        duration_days = self.duration_days

        certificate_type: str | Unset = UNSET
        if not isinstance(self.certificate_type, Unset):
            certificate_type = self.certificate_type.value

        k_8_s_namespace = self.k_8_s_namespace

        k_8_s_resource = self.k_8_s_resource

        san_dns: list[str] | Unset = UNSET
        if not isinstance(self.san_dns, Unset):
            san_dns = self.san_dns

        san_ip: list[str] | Unset = UNSET
        if not isinstance(self.san_ip, Unset):
            san_ip = self.san_ip

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "csrPem": csr_pem,
                "requestUid": request_uid,
            }
        )
        if duration_days is not UNSET:
            field_dict["durationDays"] = duration_days
        if certificate_type is not UNSET:
            field_dict["certificateType"] = certificate_type
        if k_8_s_namespace is not UNSET:
            field_dict["k8sNamespace"] = k_8_s_namespace
        if k_8_s_resource is not UNSET:
            field_dict["k8sResource"] = k_8_s_resource
        if san_dns is not UNSET:
            field_dict["sanDns"] = san_dns
        if san_ip is not UNSET:
            field_dict["sanIp"] = san_ip

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        csr_pem = d.pop("csrPem")

        request_uid = d.pop("requestUid")

        duration_days = d.pop("durationDays", UNSET)

        _certificate_type = d.pop("certificateType", UNSET)
        certificate_type: PostExternalSignBodyCertificateType | Unset
        if isinstance(_certificate_type, Unset):
            certificate_type = UNSET
        else:
            certificate_type = PostExternalSignBodyCertificateType(_certificate_type)

        k_8_s_namespace = d.pop("k8sNamespace", UNSET)

        k_8_s_resource = d.pop("k8sResource", UNSET)

        san_dns = cast(list[str], d.pop("sanDns", UNSET))

        san_ip = cast(list[str], d.pop("sanIp", UNSET))

        post_external_sign_body = cls(
            csr_pem=csr_pem,
            request_uid=request_uid,
            duration_days=duration_days,
            certificate_type=certificate_type,
            k_8_s_namespace=k_8_s_namespace,
            k_8_s_resource=k_8_s_resource,
            san_dns=san_dns,
            san_ip=san_ip,
        )

        post_external_sign_body.additional_properties = d
        return post_external_sign_body

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
