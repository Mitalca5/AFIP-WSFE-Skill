"""Build WSFEv1 payloads without performing network calls."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from .codes import CURRENCY_PESOS, DOC_TYPE_CUIT, IVA_RATES, VOUCHER_TYPES
from .validation import validate_config, validate_invoice_request

CENT = Decimal("0.01")


def money(value: int | float | str | Decimal) -> Decimal:
    return Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)


def build_fe_cae_request(
    config: dict[str, Any],
    request: dict[str, Any],
    *,
    token: str = "DRY_RUN_TOKEN",
    sign: str = "DRY_RUN_SIGN",
    next_number: int | None = None,
    today: str | None = None,
) -> dict[str, Any]:
    validate_config(config)
    validate_invoice_request(request)

    issuer = config["issuer"]
    voucher_type = request["voucher_type"]
    number = next_number if next_number is not None else int(request.get("voucher_number", 1))
    voucher_date = request.get("voucher_date") or today or datetime.now().strftime("%Y%m%d")

    amounts = calculate_amounts(request)
    detail: dict[str, Any] = {
        "Concepto": request["concept"],
        "DocTipo": DOC_TYPE_CUIT,
        "DocNro": int(request["receiver"]["cuit"]),
        "CbteDesde": number,
        "CbteHasta": number,
        "CbteFch": voucher_date,
        "ImpTotal": float(amounts["total"]),
        "ImpTotConc": 0.0,
        "ImpNeto": float(amounts["net"]),
        "ImpOpEx": float(amounts["exempt"]),
        "ImpIVA": float(amounts["vat"]),
        "ImpTrib": 0.0,
        "MonId": request.get("currency", CURRENCY_PESOS),
        "MonCotiz": float(money(request.get("currency_rate", 1))),
        "CondicionIVAReceptorId": request["receiver_iva_condition"],
    }

    if request["concept"] in {2, 3}:
        detail["FchServDesde"] = request["service_from"]
        detail["FchServHasta"] = request["service_to"]
        detail["FchVtoPago"] = request["payment_due"]

    if amounts["vat"] > 0:
        detail["Iva"] = {
            "AlicIva": [
                {
                    "Id": request.get("iva_rate_id", 5),
                    "BaseImp": float(amounts["net"]),
                    "Importe": float(amounts["vat"]),
                }
            ]
        }

    if voucher_type in {3, 8, 13}:
        associated = request["associated_voucher"]
        detail["CbtesAsoc"] = {
            "CbteAsoc": [
                {
                    "Tipo": associated["type"],
                    "PtoVta": associated["point_of_sale"],
                    "Nro": associated["number"],
                    **({"CbteFch": associated["date"]} if "date" in associated else {}),
                }
            ]
        }

    return {
        "Auth": {"Token": token, "Sign": sign, "Cuit": int(issuer["cuit"])},
        "FeCAEReq": {
            "FeCabReq": {
                "CantReg": 1,
                "PtoVta": issuer["point_of_sale"],
                "CbteTipo": voucher_type,
            },
            "FeDetReq": [{"FECAEDetRequest": detail}],
        },
    }


def calculate_amounts(request: dict[str, Any]) -> dict[str, Decimal]:
    voucher_type = request["voucher_type"]
    gross_items = sum(
        money(money(item["quantity"]) * money(item["unit_price"])) for item in request["items"]
    )
    exempt = money(gross_items) if request.get("operation_exempt") else Decimal("0.00")

    if exempt:
        return {"net": Decimal("0.00"), "vat": Decimal("0.00"), "exempt": exempt, "total": exempt}

    if voucher_type in {1, 2, 3} or request.get("discriminate_vat"):
        rate = Decimal(str(IVA_RATES[request.get("iva_rate_id", 5)]))
        vat = money(gross_items * rate)
        total = money(gross_items + vat)
        return {"net": money(gross_items), "vat": vat, "exempt": Decimal("0.00"), "total": total}

    return {
        "net": money(gross_items),
        "vat": Decimal("0.00"),
        "exempt": Decimal("0.00"),
        "total": money(gross_items),
    }


def summarize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    header = payload["FeCAEReq"]["FeCabReq"]
    detail = payload["FeCAEReq"]["FeDetReq"][0]["FECAEDetRequest"]
    return {
        "voucher_type": VOUCHER_TYPES.get(header["CbteTipo"], f"Tipo {header['CbteTipo']}"),
        "point_of_sale": header["PtoVta"],
        "number": detail["CbteDesde"],
        "total": detail["ImpTotal"],
        "receiver_doc": detail["DocNro"],
        "dry_run": payload["Auth"]["Token"] == "DRY_RUN_TOKEN",
    }
