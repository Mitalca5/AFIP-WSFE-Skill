"""WSFEv1 live client helpers. Importing this module does not perform network calls."""

from __future__ import annotations

import ssl
from pathlib import Path
from typing import Any

from .payload import build_fe_cae_request

WSFE_ENDPOINTS = {
    "homologation": "https://wswhomo.afip.gov.ar/wsfev1/service.asmx",
    "production": "https://servicios1.afip.gov.ar/wsfev1/service.asmx",
}


def create_client(environment: str, wsdl_path: str | None = None) -> Any:
    try:
        import requests
        import urllib3
        from requests.adapters import HTTPAdapter
        from zeep import Client, Settings, Transport
    except ImportError as exc:
        raise RuntimeError("live mode requires optional dependency group: pip install '.[soap]'") from exc

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    class AfipSslAdapter(HTTPAdapter):
        def init_poolmanager(self, *args: Any, **kwargs: Any) -> None:
            context = ssl.create_default_context()
            context.set_ciphers("DEFAULT:@SECLEVEL=1")
            context.check_hostname = True
            context.verify_mode = ssl.CERT_REQUIRED
            context.load_default_certs()
            kwargs["ssl_context"] = context
            return super().init_poolmanager(*args, **kwargs)

    session = requests.Session()
    session.mount("https://", AfipSslAdapter())
    transport = Transport(session=session)

    if wsdl_path:
        wsdl = Path(wsdl_path).expanduser()
        if not wsdl.exists():
            raise FileNotFoundError(f"WSDL not found: {wsdl}")
        wsdl_url = wsdl.as_uri()
    else:
        wsdl_url = WSFE_ENDPOINTS[environment] + "?wsdl"
    return Client(wsdl_url, transport=transport, settings=Settings(strict=False, xml_huge_tree=True))


def get_next_number(client: Any, token: str, sign: str, cuit: str, point_of_sale: int, voucher_type: int) -> int:
    result = client.service.FECompUltimoAutorizado(
        Auth={"Token": token, "Sign": sign, "Cuit": int(cuit)},
        PtoVta=point_of_sale,
        CbteTipo=voucher_type,
    )
    return int(result.CbteNro) + 1


def request_cae(
    client: Any,
    config: dict[str, Any],
    request: dict[str, Any],
    *,
    token: str,
    sign: str,
) -> Any:
    issuer = config["issuer"]
    next_number = get_next_number(
        client,
        token,
        sign,
        issuer["cuit"],
        issuer["point_of_sale"],
        request["voucher_type"],
    )
    payload = build_fe_cae_request(
        config,
        request,
        token=token,
        sign=sign,
        next_number=next_number,
    )
    return client.service.FECAESolicitar(**payload)

