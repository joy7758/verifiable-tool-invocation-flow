from __future__ import annotations

from verifiable_tool_invocation_flow.signer import ReceiptSigner


def test_sign_and_verify_mapping_success() -> None:
    signer = ReceiptSigner.generate_demo()
    payload = {
        "receipt_id": "receipt-demo-001",
        "action": "read_metadata",
        "signature_alg": "Ed25519",
    }

    signature = signer.sign_mapping(payload)

    assert signer.verify_mapping(payload, signature)


def test_tampered_mapping_fails_verification() -> None:
    signer = ReceiptSigner.generate_demo()
    payload = {
        "receipt_id": "receipt-demo-001",
        "action": "read_metadata",
        "signature_alg": "Ed25519",
    }
    signature = signer.sign_mapping(payload)
    tampered_payload = {**payload, "action": "write_metadata"}

    assert not signer.verify_mapping(tampered_payload, signature)


def test_signature_field_is_excluded_from_signed_payload() -> None:
    signer = ReceiptSigner.generate_demo()
    payload = {
        "receipt_id": "receipt-demo-001",
        "action": "read_metadata",
        "signature_alg": "Ed25519",
        "issuer": "demo-signer",
    }
    signature = signer.sign_mapping(payload)
    signed_payload = {**payload, "signature": signature}

    assert signer.verify_mapping(signed_payload, signature)

    tampered_payload = {**signed_payload, "issuer": "other-signer"}
    assert not signer.verify_mapping(tampered_payload, signature)


def test_verify_with_wrong_key_fails() -> None:
    signer_a = ReceiptSigner.generate_demo(public_key_id="key-a")
    signer_b = ReceiptSigner.generate_demo(public_key_id="key-b")
    payload = {
        "receipt_id": "receipt-demo-001",
        "action": "read_metadata",
        "signature_alg": "Ed25519",
    }
    signature = signer_a.sign_mapping(payload)

    assert not signer_b.verify_mapping(payload, signature, public_key_pem=signer_b.public_key_pem())


def test_malformed_signature_returns_false() -> None:
    signer = ReceiptSigner.generate_demo()
    payload = {
        "receipt_id": "receipt-demo-001",
        "action": "read_metadata",
        "signature_alg": "Ed25519",
    }

    assert not signer.verify_mapping(payload, "not-base64")
    assert not signer.verify_mapping(payload, "base64:not-valid-base64")
    assert not signer.verify_mapping(payload, "")


def test_public_key_pem_roundtrip() -> None:
    signer = ReceiptSigner.generate_demo()
    payload = {
        "receipt_id": "receipt-demo-001",
        "action": "read_metadata",
        "signature_alg": "Ed25519",
    }
    signature = signer.sign_mapping(payload)
    public_key_pem = signer.public_key_pem()

    assert signer.verify_mapping(payload, signature, public_key_pem=public_key_pem)
