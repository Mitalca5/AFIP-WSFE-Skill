# AFIP/ARCA WSFEv1 Codes

Common codes used by WSFEv1. Confirm against current AFIP/ARCA documentation before
production use.

## Voucher Types

| Code | Type |
| ---: | --- |
| 1 | Factura A |
| 2 | Nota de Debito A |
| 3 | Nota de Credito A |
| 6 | Factura B |
| 7 | Nota de Debito B |
| 8 | Nota de Credito B |
| 11 | Factura C |
| 12 | Nota de Debito C |
| 13 | Nota de Credito C |

## Concepts

| Code | Concept | Extra required fields |
| ---: | --- | --- |
| 1 | Productos | None |
| 2 | Servicios | `FchServDesde`, `FchServHasta`, `FchVtoPago` |
| 3 | Productos y Servicios | `FchServDesde`, `FchServHasta`, `FchVtoPago` |

## Receiver IVA Conditions

| Code | Condition |
| ---: | --- |
| 1 | Responsable Inscripto |
| 4 | Sujeto Exento |
| 5 | Consumidor Final |
| 6 | Responsable Monotributo |
| 7 | Sujeto No Categorizado |
| 13 | Monotributista Social |
| 15 | Monotributo Trabajador |

## IVA Rates

| Code | Rate |
| ---: | ---: |
| 3 | 0% |
| 4 | 10.5% |
| 5 | 21% |
| 6 | 27% |
| 8 | 5% |
| 9 | 2.5% |

