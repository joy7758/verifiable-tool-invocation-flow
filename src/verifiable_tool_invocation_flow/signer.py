"""Ed25519 signing helpers for canonical JSON payloads."""

from __future__ import annotations

import base64
import binascii
from collections.abc import Mapping
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from .canonical import canonical_bytes


class ReceiptSigner:
    """Sign and verify canonical payloads with an Ed25519 keypair."""

    def __init__(
        self,
        private_key: Ed25519PrivateKey,
        *,
        public_key_id: str = "demo-ed25519-key-001",
    ) -> None:
        self._private_key = private_key
        self._public_key = private_key.public_key()
        self._public_key_id = public_key_id

    @classmethod
    def generate_demo(cls, public_key_id: str = "demo-ed25519-key-001") -> "ReceiptSigner":
        """Generate an in-memory demo signer for local tests and examples."""
        return cls(Ed25519PrivateKey.generate(), public_key_id=public_key_id)

    @classmethod
    def from_private_key_pem(
        cls,
        private_key_pem: bytes,
        password: bytes | None = None,
        public_key_id: str = "demo-ed25519-key-001",
    ) -> "ReceiptSigner":
        """Load an Ed25519 private key from PEM bytes."""
        loaded_key = serialization.load_pem_private_key(private_key_pem, password=password)
        if not isinstance(loaded_key, Ed25519PrivateKey):
            raise TypeError("Expected an Ed25519 private key PEM")
        return cls(loaded_key, public_key_id=public_key_id)

    def private_key_pem(self) -> bytes:
        """Export the private key as unencrypted PKCS#8 PEM for local demo use."""
        return self._private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

    def public_key_pem(self) -> bytes:
        """Export the public key as SubjectPublicKeyInfo PEM."""
        return self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    def public_key_id(self) -> str:
        """Return the configured public key identifier."""
        return self._public_key_id

    def sign_bytes(self, payload: bytes) -> str:
        """Sign a raw byte payload and return a base64-prefixed signature."""
        signature = self._private_key.sign(payload)
        return self._encode_signature(signature)

    def sign_mapping(self, payload: dict[str, Any]) -> str:
        """Sign a mapping after canonicalization and top-level signature removal."""
        return self.sign_bytes(self._canonical_mapping_bytes(payload))

    def verify_bytes(
        self,
        payload: bytes,
        signature: str,
        public_key_pem: bytes | None = None,
    ) -> bool:
        """Verify a raw byte payload without raising signature errors to callers."""
        decoded_signature = self._decode_signature(signature)
        if decoded_signature is None:
            return False

        try:
            public_key = self._load_public_key(public_key_pem)
            public_key.verify(decoded_signature, payload)
        except (InvalidSignature, TypeError, ValueError):
            return False
        return True

    def verify_mapping(
        self,
        payload: dict[str, Any],
        signature: str,
        public_key_pem: bytes | None = None,
    ) -> bool:
        """Verify a mapping after canonicalization and top-level signature removal."""
        return self.verify_bytes(self._canonical_mapping_bytes(payload), signature, public_key_pem)

    def _canonical_mapping_bytes(self, payload: Mapping[str, Any]) -> bytes:
        return canonical_bytes(self._strip_signature_field(payload))

    def _strip_signature_field(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in payload.items() if key != "signature"}

    def _load_public_key(self, public_key_pem: bytes | None) -> Ed25519PublicKey:
        if public_key_pem is None:
            return self._public_key

        loaded_key = serialization.load_pem_public_key(public_key_pem)
        if not isinstance(loaded_key, Ed25519PublicKey):
            raise TypeError("Expected an Ed25519 public key PEM")
        return loaded_key

    def _encode_signature(self, signature: bytes) -> str:
        return f"base64:{base64.b64encode(signature).decode('ascii')}"

    def _decode_signature(self, signature: str) -> bytes | None:
        if not signature or not signature.startswith("base64:"):
            return None

        encoded_signature = signature[len("base64:") :]
        try:
            return base64.b64decode(encoded_signature, validate=True)
        except (binascii.Error, ValueError):
            return None
