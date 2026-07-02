"""Validation for sanitized AFIP/ARCA WSFE requests."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any

from .codes import CONCEPTS, IVA_CONDITIONS, IVA_RATES, VOUCHER_TYPES


class ValidationError(ValueError):
    """Raised when a config or invoice request is invalid."""


CUIT_RE = re.compile(r"^\d{11}$")
DATE_RE = re.compile(r"^\d{8}$")


def validate_cuit(value: Any, field: str) -> None:
    if not isinstance(value, str) or not CUIT_RE.fullmatch(value):
        raise ValidationError(f"{field} must be an 11 digit CUIT string")


def validate_yyyymmdd(value: Any, field: str) -> None:
    if not isinstance(value, str) or not DATE_RE.fullmatch(value):
        raise ValidationError(f"{field} must be YYYYMMDD")
    try:
        datetime.strptime(value, "%Y%m%d")
    except ValueError as exc:
        raise ValidationError(f"{field} is not a valid date") from exc


def validate_config(config: dict[str, Any], *, live: bool = False) -> None:
    issuer = _require_object(config, "issuer")
    validate_cuit(issuer.get("cuit"), "issuer.cuit")
    _require_int(issuer, "point_of_sale", minimum=1)

    environment = config.get("environment", "homologation")
    if environment not in {"homologation", "production"}:
        raise ValidationError("environment must be homologation or production")

    if live:
        if config.get("confirm_live") is not True:
            raise ValidationError("live mode requires confirm_live: true")
        for key in ("certificate_path", "private_key_path"):
            value = issuer.get(key)
            if not isinstance(value, str) or not value:
                raise ValidationError(f"issuer.{key} is required in live mode")
            if not Path(value).expanduser().exists():
                raise ValidationError(f"issuer.{key} does not exist")


def validate_invoice_request(request: dict[str, Any]) -> None:
    _require_int(request, "voucher_type", allowed=set(VOUCHER_TYPES))
    concept = _require_int(request, "concept", allowed=set(CONCEPTS))
    _require_int(request, "receiver_iva_condition", allowed=set(IVA_CONDITIONS))

    receiver = _require_object(request, "receiver")
    validate_cuit(receiver.get("cuit"), "receiver.cuit")

    items = request.get("items")
    if not isinstance(items, list) or not items:
        raise ValidationError("items must be a non-empty list")
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValidationError(f"items[{index}] must be an object")
        if not isinstance(item.get("description"), str) or not item["description"].strip():
            raise ValidationError(f"items[{index}].description is required")
        _require_number(item, "quantity", minimum=0)
        _require_number(item, "unit_price", minimum=0)

    if concept in {2, 3}:
        for field in ("service_from", "service_to", "payment_due"):
            validate_yyyymmdd(request.get(field), field)

    if "voucher_date" in request:
        validate_yyyymmdd(request["voucher_date"], "voucher_date")

    if "iva_rate_id" in request:
        _require_int(request, "iva_rate_id", allowed=set(IVA_RATES))

    if request["voucher_type"] in {3, 8, 13}:
        associated = _require_object(request, "associated_voucher")
        _require_int(associated, "type", allowed=set(VOUCHER_TYPES))
        _require_int(associated, "point_of_sale", minimum=1)
        _require_int(associated, "number", minimum=1)
        if "date" in associated:
            validate_yyyymmdd(associated["date"], "associated_voucher.date")


def _require_object(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        raise ValidationError(f"{key} must be an object")
    return value


def _require_int(
    data: dict[str, Any],
    key: str,
    *,
    minimum: int | None = None,
    allowed: set[int] | None = None,
) -> int:
    value = data.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValidationError(f"{key} must be an integer")
    if minimum is not None and value < minimum:
        raise ValidationError(f"{key} must be >= {minimum}")
    if allowed is not None and value not in allowed:
        raise ValidationError(f"{key} is not an allowed code")
    return value


def _require_number(data: dict[str, Any], key: str, *, minimum: float) -> float:
    value = data.get(key)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValidationError(f"{key} must be a number")
    if value < minimum:
        raise ValidationError(f"{key} must be >= {minimum}")
    return float(value)

