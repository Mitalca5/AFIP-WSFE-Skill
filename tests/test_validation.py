import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from open_afip_wsfe.validation import ValidationError, validate_config, validate_invoice_request


class ValidationTest(unittest.TestCase):
    def test_rejects_invalid_cuit(self):
        with self.assertRaises(ValidationError):
            validate_config({"issuer": {"cuit": "20-11111111-2", "point_of_sale": 1}})

    def test_services_require_dates(self):
        request = {
            "voucher_type": 6,
            "concept": 2,
            "receiver": {"cuit": "20222222223"},
            "receiver_iva_condition": 5,
            "items": [{"description": "Servicio", "quantity": 1, "unit_price": 10}],
        }
        with self.assertRaises(ValidationError):
            validate_invoice_request(request)

    def test_live_requires_explicit_confirmation(self):
        config = {
            "environment": "homologation",
            "confirm_live": False,
            "issuer": {"cuit": "20111111112", "point_of_sale": 1},
        }
        with self.assertRaises(ValidationError):
            validate_config(config, live=True)


if __name__ == "__main__":
    unittest.main()
