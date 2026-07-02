import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from open_afip_wsfe.payload import build_fe_cae_request, calculate_amounts


CONFIG = {
    "environment": "homologation",
    "confirm_live": False,
    "issuer": {"cuit": "20111111112", "point_of_sale": 1, "iva_condition": 1},
}

REQUEST_A = {
    "voucher_type": 1,
    "concept": 2,
    "voucher_date": "20260701",
    "service_from": "20260701",
    "service_to": "20260731",
    "payment_due": "20260810",
    "receiver": {"cuit": "20222222223"},
    "receiver_iva_condition": 1,
    "iva_rate_id": 5,
    "items": [{"description": "Servicio ficticio", "quantity": 1, "unit_price": 1000.0}],
}


class PayloadTest(unittest.TestCase):
    def test_calculates_factura_a_vat(self):
        amounts = calculate_amounts(REQUEST_A)
        self.assertEqual(str(amounts["net"]), "1000.00")
        self.assertEqual(str(amounts["vat"]), "210.00")
        self.assertEqual(str(amounts["total"]), "1210.00")

    def test_builds_fe_cae_request(self):
        payload = build_fe_cae_request(CONFIG, REQUEST_A, next_number=7)
        header = payload["FeCAEReq"]["FeCabReq"]
        detail = payload["FeCAEReq"]["FeDetReq"][0]["FECAEDetRequest"]
        self.assertEqual(payload["Auth"]["Cuit"], 20111111112)
        self.assertEqual(header["PtoVta"], 1)
        self.assertEqual(header["CbteTipo"], 1)
        self.assertEqual(detail["CbteDesde"], 7)
        self.assertEqual(detail["ImpIVA"], 210.0)
        self.assertEqual(detail["Iva"]["AlicIva"][0]["Id"], 5)
        self.assertEqual(detail["FchVtoPago"], "20260810")

    def test_builds_credit_note_association(self):
        request = {
            **REQUEST_A,
            "voucher_type": 3,
            "associated_voucher": {"type": 1, "point_of_sale": 1, "number": 6, "date": "20260701"},
        }
        payload = build_fe_cae_request(CONFIG, request, next_number=8)
        detail = payload["FeCAEReq"]["FeDetReq"][0]["FECAEDetRequest"]
        assoc = detail["CbtesAsoc"]["CbteAsoc"][0]
        self.assertEqual(assoc["Tipo"], 1)
        self.assertEqual(assoc["Nro"], 6)


if __name__ == "__main__":
    unittest.main()
