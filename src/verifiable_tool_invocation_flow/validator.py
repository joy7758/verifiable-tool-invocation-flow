"""Independent execution receipt validation helpers and CLI."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import ValidationError as JSONSchemaValidationError
from jsonschema import validate as validate_jsonschema
from pydantic import ValidationError as PydanticValidationError

from .hashing import sha256_digest
from .models import ExecutionRequest, PolicySnapshot, ToolManifest, VerificationReport
from .policy_checker import PolicyDecision, evaluate_policy
from .receipt_builder import DEFAULT_AUDIENCE, build_pre_execution_commitment, isoformat_z
from .signer import ReceiptSigner


def validate_receipt(
    receipt: Mapping[str, Any],
    evidence_bundle: Mapping[str, Any],
    public_key_pem: bytes,
    *,
    audience: str = DEFAULT_AUDIENCE,
    checked_at: datetime | None = None,
    replay_cache_path: Path | None = None,
    update_replay_cache: bool = True,
) -> dict[str, Any]:
    """Validate a signed receipt against its evidence bundle without relying on any Flow runtime."""
    errors: list[str] = []
    warnings: list[str] = []

    receipt_mapping = dict(receipt) if isinstance(receipt, Mapping) else {}
    evidence_mapping = dict(evidence_bundle) if isinstance(evidence_bundle, Mapping) else {}

    checked_at_value = _coerce_checked_at(checked_at, errors)
    checked_at_string = isoformat_z(checked_at_value)

    schema_valid = _validate_receipt_schema(receipt_mapping, errors)

    request_payload = _expect_mapping(evidence_mapping.get("request"), "request", errors)
    policy_payload = _expect_mapping(evidence_mapping.get("policy"), "policy", errors)
    tool_manifest_payload = _expect_mapping(evidence_mapping.get("tool_manifest"), "tool_manifest", errors)
    tool_input_payload = _expect_mapping(evidence_mapping.get("tool_input"), "tool_input", errors)
    tool_output_payload = _expect_mapping(evidence_mapping.get("tool_output"), "tool_output", errors)

    input_hash_match, input_hash = _hash_match(
        "input_hash", request_payload, receipt_mapping.get("input_hash"), errors
    )
    policy_hash_match, policy_hash = _hash_match(
        "policy_hash", policy_payload, receipt_mapping.get("policy_hash"), errors
    )
    tool_manifest_hash_match, tool_manifest_hash = _hash_match(
        "tool_manifest_hash", tool_manifest_payload, receipt_mapping.get("tool_manifest_hash"), errors
    )
    tool_input_hash_match, tool_input_hash = _hash_match(
        "tool_input_hash", tool_input_payload, receipt_mapping.get("tool_input_hash"), errors
    )
    tool_output_hash_match, tool_output_hash = _hash_match(
        "tool_output_hash", tool_output_payload, receipt_mapping.get("tool_output_hash"), errors
    )

    result_hash_match = (
        isinstance(receipt_mapping.get("result_hash"), str)
        and tool_output_hash is not None
        and receipt_mapping.get("result_hash") == tool_output_hash
        and receipt_mapping.get("result_hash") == receipt_mapping.get("tool_output_hash")
    )
    if not result_hash_match:
        errors.append("result_hash_mismatch")

    pre_execution_commitment_match = _validate_pre_execution_commitment(
        receipt_mapping,
        input_hash=input_hash,
        policy_hash=policy_hash,
        tool_manifest_hash=tool_manifest_hash,
        tool_input_hash=tool_input_hash,
        errors=errors,
    )

    request_binding_match = _validate_request_binding(receipt_mapping, request_payload, errors)
    audience_match = isinstance(receipt_mapping.get("audience"), str) and receipt_mapping.get("audience") == audience
    if not audience_match:
        errors.append("audience_mismatch")

    time_window_valid = _validate_time_window(
        receipt_mapping.get("issued_at"),
        receipt_mapping.get("expires_at"),
        checked_at_value,
        errors,
    )

    policy_decision_valid = _validate_policy_decision(
        receipt_mapping,
        request_payload,
        policy_payload,
        tool_manifest_payload,
        errors,
    )

    signature_valid = _validate_signature(receipt_mapping, public_key_pem, errors)

    replay_check_performed = replay_cache_path is not None
    replay_detected = False
    replay_cache: dict[str, str] = {}
    replay_key = _build_replay_key(receipt_mapping)
    if replay_cache_path is not None:
        replay_cache = _load_replay_cache(replay_cache_path, errors, warnings)
        replay_detected = replay_key in replay_cache
        if replay_detected:
            errors.append("replay_detected")

    provisional_valid = all(
        [
            schema_valid,
            input_hash_match,
            policy_hash_match,
            tool_manifest_hash_match,
            tool_input_hash_match,
            tool_output_hash_match,
            result_hash_match,
            pre_execution_commitment_match,
            policy_decision_valid,
            signature_valid,
            time_window_valid,
            audience_match,
            request_binding_match,
        ]
    )

    if replay_cache_path is not None and update_replay_cache and provisional_valid and not replay_detected:
        replay_cache[replay_key] = checked_at_string
        _write_replay_cache(replay_cache_path, replay_cache)

    verdict = (
        "valid"
        if all(
            [
                schema_valid,
                input_hash_match,
                policy_hash_match,
                tool_manifest_hash_match,
                tool_input_hash_match,
                tool_output_hash_match,
                result_hash_match,
                pre_execution_commitment_match,
                policy_decision_valid,
                signature_valid,
                time_window_valid,
                not replay_detected,
                audience_match,
                request_binding_match,
            ]
        )
        else "invalid"
    )

    report = VerificationReport(
        receipt_id=_string_or_empty(receipt_mapping.get("receipt_id")),
        execution_id=_string_or_empty(receipt_mapping.get("execution_id")),
        profile_version=_string_or_empty(receipt_mapping.get("profile_version")),
        checked_at=checked_at_string,
        schema_valid=schema_valid,
        input_hash_match=input_hash_match,
        policy_hash_match=policy_hash_match,
        tool_manifest_hash_match=tool_manifest_hash_match,
        tool_input_hash_match=tool_input_hash_match,
        tool_output_hash_match=tool_output_hash_match,
        result_hash_match=result_hash_match,
        pre_execution_commitment_match=pre_execution_commitment_match,
        policy_decision_valid=policy_decision_valid,
        signature_valid=signature_valid,
        time_window_valid=time_window_valid,
        replay_check_performed=replay_check_performed,
        replay_detected=replay_detected,
        audience_match=audience_match,
        request_binding_match=request_binding_match,
        verdict=verdict,
        errors=errors,
        warnings=warnings,
    )
    return report.model_dump(mode="json")


def load_json_file(path: Path) -> dict[str, Any]:
    """Load a JSON object from disk."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def write_json_file(path: Path, payload: Mapping[str, Any]) -> None:
    """Write a JSON object to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for independent receipt validation."""
    parser = argparse.ArgumentParser(description="Validate a signed execution receipt against an evidence bundle.")
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--public-key", required=True, type=Path)
    parser.add_argument("--audience", default=DEFAULT_AUDIENCE)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--replay-cache", type=Path)
    args = parser.parse_args(argv)

    receipt = load_json_file(args.receipt)
    evidence_bundle = load_json_file(args.evidence)
    public_key_pem = args.public_key.read_bytes()
    report = validate_receipt(
        receipt,
        evidence_bundle,
        public_key_pem,
        audience=args.audience,
        replay_cache_path=args.replay_cache,
    )

    if args.out is not None:
        write_json_file(args.out, report)

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["verdict"] == "valid" else 1


def _validate_receipt_schema(receipt: Mapping[str, Any], errors: list[str]) -> bool:
    schema_path = Path(__file__).resolve().parents[2] / "schemas" / "execution_receipt.schema.json"
    schema = load_json_file(schema_path)
    try:
        validate_jsonschema(instance=dict(receipt), schema=schema)
    except JSONSchemaValidationError as exc:
        errors.append(f"schema_invalid: {exc.message}")
        return False
    return True


def _expect_mapping(value: Any, label: str, errors: list[str]) -> dict[str, Any] | None:
    if isinstance(value, Mapping):
        return dict(value)
    errors.append(f"invalid_evidence_{label}")
    return None


def _hash_match(
    label: str,
    payload: Mapping[str, Any] | None,
    actual_hash: Any,
    errors: list[str],
) -> tuple[bool, str | None]:
    if payload is None:
        errors.append(f"{label}_source_missing")
        return False, None
    try:
        expected_hash = sha256_digest(payload)
    except Exception as exc:
        errors.append(f"{label}_recompute_failed: {exc}")
        return False, None
    match = isinstance(actual_hash, str) and actual_hash == expected_hash
    if not match:
        errors.append(f"{label}_mismatch")
    return match, expected_hash


def _validate_pre_execution_commitment(
    receipt: Mapping[str, Any],
    *,
    input_hash: str | None,
    policy_hash: str | None,
    tool_manifest_hash: str | None,
    tool_input_hash: str | None,
    errors: list[str],
) -> bool:
    if not all([input_hash, policy_hash, tool_manifest_hash, tool_input_hash]):
        errors.append("pre_execution_commitment_inputs_missing")
        return False

    required_values = [
        receipt.get("request_id"),
        receipt.get("execution_id"),
        receipt.get("nonce"),
        receipt.get("audience"),
    ]
    if not all(isinstance(value, str) for value in required_values):
        errors.append("pre_execution_commitment_fields_missing")
        return False

    expected = build_pre_execution_commitment(
        request_id=required_values[0],
        execution_id=required_values[1],
        nonce=required_values[2],
        audience=required_values[3],
        input_hash=input_hash,
        policy_hash=policy_hash,
        tool_manifest_hash=tool_manifest_hash,
        tool_input_hash=tool_input_hash,
    )
    match = receipt.get("pre_execution_commitment") == expected
    if not match:
        errors.append("pre_execution_commitment_mismatch")
    return match


def _validate_request_binding(
    receipt: Mapping[str, Any],
    request_payload: Mapping[str, Any] | None,
    errors: list[str],
) -> bool:
    if request_payload is None:
        errors.append("request_binding_source_missing")
        return False

    fields = ["request_id", "agent_id", "resource_id", "action", "tool_id"]
    match = all(receipt.get(field) == request_payload.get(field) for field in fields)
    if not match:
        errors.append("request_binding_mismatch")
    return match


def _validate_time_window(
    issued_at: Any,
    expires_at: Any,
    checked_at: datetime,
    errors: list[str],
) -> bool:
    try:
        issued_at_value = _parse_datetime(issued_at)
        expires_at_value = _parse_datetime(expires_at)
    except ValueError as exc:
        errors.append(f"time_window_parse_failed: {exc}")
        return False

    match = issued_at_value <= checked_at <= expires_at_value
    if not match:
        errors.append("time_window_invalid")
    return match


def _validate_policy_decision(
    receipt: Mapping[str, Any],
    request_payload: Mapping[str, Any] | None,
    policy_payload: Mapping[str, Any] | None,
    tool_manifest_payload: Mapping[str, Any] | None,
    errors: list[str],
) -> bool:
    if request_payload is None or policy_payload is None or tool_manifest_payload is None:
        errors.append("policy_decision_source_missing")
        return False

    try:
        request = ExecutionRequest.model_validate(request_payload)
        policy = PolicySnapshot.model_validate(policy_payload)
        tool_manifest = ToolManifest.model_validate(tool_manifest_payload)
        current_decision = evaluate_policy(request, policy, tool_manifest)
        receipt_decision = PolicyDecision.model_validate(receipt.get("policy_decision"))
    except (PydanticValidationError, TypeError) as exc:
        errors.append(f"policy_decision_rebuild_failed: {exc}")
        return False

    tool_call = receipt.get("tool_call")
    tool_status = tool_call.get("status") if isinstance(tool_call, Mapping) else None
    if receipt_decision.allowed is False and tool_status == "success":
        errors.append("policy_decision_denied_but_execution_succeeded")
        return False

    valid = current_decision.allowed is True and receipt_decision.allowed is True and receipt_decision == current_decision
    if not valid:
        errors.append("policy_decision_invalid")
    return valid


def _validate_signature(receipt: Mapping[str, Any], public_key_pem: bytes, errors: list[str]) -> bool:
    signature = receipt.get("signature")
    if not isinstance(signature, str):
        errors.append("signature_missing_or_invalid")
        return False

    valid = ReceiptSigner.generate_demo().verify_mapping(dict(receipt), signature, public_key_pem=public_key_pem)
    if not valid:
        errors.append("signature_invalid")
    return valid


def _coerce_checked_at(checked_at: datetime | None, errors: list[str]) -> datetime:
    if checked_at is None:
        return datetime.now(timezone.utc).replace(microsecond=0)
    if checked_at.tzinfo is None or checked_at.utcoffset() is None:
        errors.append("checked_at_not_timezone_aware")
        return checked_at.replace(tzinfo=timezone.utc)
    return checked_at.astimezone(timezone.utc)


def _parse_datetime(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ValueError("expected ISO-8601 string")
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("expected timezone-aware datetime")
    return parsed.astimezone(timezone.utc)


def _build_replay_key(receipt: Mapping[str, Any]) -> str:
    return f"{_string_or_empty(receipt.get('execution_id'))}:{_string_or_empty(receipt.get('nonce'))}"


def _load_replay_cache(path: Path, errors: list[str], warnings: list[str]) -> dict[str, str]:
    if not path.exists():
        return {}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        warnings.append(f"replay_cache_load_failed: {exc}")
        return {}

    if not isinstance(data, dict):
        warnings.append("replay_cache_not_object")
        return {}

    return {str(key): str(value) for key, value in data.items()}


def _write_replay_cache(path: Path, payload: Mapping[str, Any]) -> None:
    write_json_file(path, payload)


def _string_or_empty(value: Any) -> str:
    return value if isinstance(value, str) else ""


if __name__ == "__main__":
    raise SystemExit(main())
