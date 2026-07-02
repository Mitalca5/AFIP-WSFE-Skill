"""WSAA authentication helpers used only in explicit live mode."""

from __future__ import annotations

import html
import os
import subprocess
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


WSAA_URLS = {
    "homologation": "https://wsaahomo.afip.gov.ar/ws/services/LoginCms",
    "production": "https://wsaa.afip.gov.ar/ws/services/LoginCms",
}


def build_login_ticket_request(service: str = "wsfe") -> str:
    now = datetime.now()
    generation = now - timedelta(minutes=5)
    expiration = now + timedelta(hours=12)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<loginTicketRequest version="1.0">
<header>
<uniqueId>{int(now.timestamp())}</uniqueId>
<generationTime>{generation.strftime("%Y-%m-%dT%H:%M:%S-03:00")}</generationTime>
<expirationTime>{expiration.strftime("%Y-%m-%dT%H:%M:%S-03:00")}</expirationTime>
</header>
<service>{service}</service>
</loginTicketRequest>"""


def sign_cms(xml: str, certificate_path: str | Path, private_key_path: str | Path) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False, encoding="utf-8") as handle:
        handle.write(xml)
        xml_path = Path(handle.name)
    cms_path = xml_path.with_suffix(".cms")
    try:
        result = subprocess.run(
            [
                "openssl",
                "cms",
                "-sign",
                "-in",
                str(xml_path),
                "-out",
                str(cms_path),
                "-signer",
                str(certificate_path),
                "-inkey",
                str(private_key_path),
                "-nodetach",
                "-outform",
                "PEM",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(f"openssl cms failed: {result.stderr.strip()}")
        content = cms_path.read_text(encoding="utf-8")
        return "".join(line for line in content.splitlines() if not line.startswith("-----"))
    finally:
        for path in (xml_path, cms_path):
            try:
                os.unlink(path)
            except FileNotFoundError:
                pass


def login_cms(config: dict[str, Any], service: str = "wsfe") -> dict[str, str]:
    try:
        import requests
        from lxml import etree
    except ImportError as exc:
        raise RuntimeError("live mode requires optional dependency group: pip install '.[soap]'") from exc

    issuer = config["issuer"]
    environment = config.get("environment", "homologation")
    xml = build_login_ticket_request(service)
    cms = sign_cms(xml, issuer["certificate_path"], issuer["private_key_path"])
    soap_body = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
<soapenv:Header/>
<soapenv:Body>
<loginCms xmlns="http://wsaa.view.sua.dvadac.desein.afip.gov">
<in0>{cms}</in0>
</loginCms>
</soapenv:Body>
</soapenv:Envelope>"""
    response = requests.post(
        WSAA_URLS[environment],
        data=soap_body,
        headers={"Content-Type": "text/xml; charset=utf-8", "SOAPAction": "urn:loginCms"},
        timeout=30,
    )
    if response.status_code != 200:
        raise RuntimeError(f"WSAA HTTP {response.status_code}")

    root = etree.fromstring(response.content)
    fault = root.find(".//{http://schemas.xmlsoap.org/soap/envelope/}Fault")
    if fault is not None:
        faultstring = fault.find(".//faultstring")
        raise RuntimeError(f"WSAA fault: {faultstring.text if faultstring is not None else 'unknown'}")

    login_return = None
    for elem in root.iter():
        if elem.tag.endswith("loginCmsReturn") and elem.text:
            login_return = elem.text
            break
    if not login_return:
        raise RuntimeError("WSAA response did not include loginCmsReturn")

    inner = etree.fromstring(html.unescape(login_return).encode("utf-8"))
    token = inner.find(".//token")
    sign = inner.find(".//sign")
    if token is None or sign is None or not token.text or not sign.text:
        raise RuntimeError("WSAA response did not include token/sign")
    return {"token": token.text, "sign": sign.text}

