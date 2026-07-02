#!/usr/bin/env python3
"""Dry-run first AFIP/ARCA WSFEv1 demo CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from open_afip_wsfe import build_fe_cae_request, load_config, load_invoice_request, summarize_payload
from open_afip_wsfe.validation import validate_config, validate_invoice_request


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build or submit an AFIP/ARCA WSFEv1 request.")
    parser.add_argument("--config", required=True, help="Path to config JSON")
    parser.add_argument("--request", required=True, help="Path to invoice request JSON")
    parser.add_argument("--live", action="store_true", help="Opt in to real WSAA/WSFE network calls")
    parser.add_argument("--wsdl", help="Optional local WSFE WSDL path for live mode")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_config(args.config)
    request = load_invoice_request(args.request)
    validate_config(config, live=args.live)
    validate_invoice_request(request)

    if not args.live:
        payload = build_fe_cae_request(config, request)
        print(json.dumps({"summary": summarize_payload(payload), "payload": payload}, indent=2, sort_keys=True))
        return 0

    from open_afip_wsfe.wsaa import login_cms
    from open_afip_wsfe.wsfe import create_client, request_cae

    ticket = login_cms(config)
    client = create_client(config.get("environment", "homologation"), args.wsdl)
    result = request_cae(client, config, request, token=ticket["token"], sign=ticket["sign"])
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

