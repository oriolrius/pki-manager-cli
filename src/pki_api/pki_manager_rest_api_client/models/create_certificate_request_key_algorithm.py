from enum import Enum


class CreateCertificateRequestKeyAlgorithm(str, Enum):
    ECDSA_P256 = "ECDSA-P256"
    ECDSA_P384 = "ECDSA-P384"
    RSA_2048 = "RSA-2048"
    RSA_4096 = "RSA-4096"

    def __str__(self) -> str:
        return str(self.value)
