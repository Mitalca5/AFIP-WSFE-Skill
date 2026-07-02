"""Common AFIP/ARCA WSFEv1 code constants."""

VOUCHER_TYPES = {
    1: "Factura A",
    2: "Nota de Debito A",
    3: "Nota de Credito A",
    6: "Factura B",
    7: "Nota de Debito B",
    8: "Nota de Credito B",
    11: "Factura C",
    12: "Nota de Debito C",
    13: "Nota de Credito C",
}

CONCEPTS = {
    1: "Productos",
    2: "Servicios",
    3: "Productos y Servicios",
}

IVA_CONDITIONS = {
    1: "Responsable Inscripto",
    4: "Sujeto Exento",
    5: "Consumidor Final",
    6: "Responsable Monotributo",
    7: "Sujeto No Categorizado",
    13: "Monotributista Social",
    15: "Monotributo Trabajador",
}

IVA_RATES = {
    3: 0.0,
    4: 0.105,
    5: 0.21,
    6: 0.27,
    8: 0.05,
    9: 0.025,
}

DOC_TYPE_CUIT = 80
CURRENCY_PESOS = "PES"

