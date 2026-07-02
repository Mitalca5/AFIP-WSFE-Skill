# Certificates And AFIP/ARCA Setup

Use this reference when a user wants to move from dry-run payload generation to live
WSAA/WSFEv1 calls and does not yet have a certificate, private key, service
authorization, or electronic point of sale.

Confirm labels and menus against the current AFIP/ARCA site before production use.
Government portals change names and navigation over time.

## What You Need

- CUIT with the required fiscal access level.
- Access to the taxpayer or an authorized representative in AFIP/ARCA.
- OpenSSL installed locally.
- A private key file kept outside the repository.
- A CSR generated from that private key.
- A certificate downloaded from AFIP/ARCA after uploading the CSR.
- WSFEv1 web service authorization for the taxpayer CUIT.
- An electronic point of sale compatible with online electronic invoicing.

## Generate A Private Key And CSR

Run these commands outside the repository, in a private directory:

```bash
openssl genrsa -out private.key 2048
openssl req -new -key private.key -out request.csr \
  -subj "/serialNumber=CUIT 20111111112, CN=Fictional Issuer"
```

Replace `20111111112` and `Fictional Issuer` with the real taxpayer CUIT and display
name in your private local environment. Do not commit the generated files.

Expected files:

```text
private.key   # Keep secret. Never commit or share.
request.csr   # Upload this to AFIP/ARCA.
```

## Upload The CSR And Download The Certificate

In AFIP/ARCA, use the digital certificate administration service for web services:

1. Sign in with the taxpayer or authorized representative.
2. Open the digital certificate administration service.
3. Create or select the relevant web service certificate entry.
4. Upload `request.csr`.
5. Download the issued certificate, usually saved locally as `certificate.crt`.

Expected private local files after this step:

```text
certificate.crt
private.key
```

Only `certificate.crt` and `private.key` are required by this project for WSAA
authentication. Keep both outside the repository; the private key is sensitive.

## Authorize WSFEv1

The taxpayer CUIT must authorize the electronic invoicing web service:

1. Open the fiscal relationship or service authorization area in AFIP/ARCA.
2. Add a new relationship for the AFIP/ARCA web service used for electronic invoicing.
3. Select WSFEv1 / online electronic invoicing web service.
4. Assign it to the taxpayer CUIT and representative as required by the portal.
5. Sign out and sign in again if the portal requires session refresh.

Without this step, WSAA may authenticate but WSFEv1 calls can still fail.

## Configure An Electronic Point Of Sale

The taxpayer also needs an electronic point of sale compatible with the voucher types
being issued:

1. Open the point of sale administration service.
2. Create or verify a point of sale for online electronic invoicing.
3. Record the point of sale number in private config as `issuer.point_of_sale`.
4. Confirm which voucher types are valid for that taxpayer and IVA condition.

Common failures from an incorrect point of sale include messages equivalent to "point
of sale not authorized" or "voucher type not enabled".

## Private Config Example

Store live config in `config.json` or `*.private.json`; both are ignored by git.

```json
{
  "environment": "homologation",
  "confirm_live": true,
  "issuer": {
    "display_name": "Private Issuer Name",
    "cuit": "20111111112",
    "point_of_sale": 1,
    "iva_condition": 1,
    "certificate_path": "/absolute/private/path/certificate.crt",
    "private_key_path": "/absolute/private/path/private.key"
  }
}
```

Use `homologation` for testing when possible. Use `production` only when the taxpayer,
certificate, web service authorization, point of sale, voucher type, receiver data,
amounts, and dates have been reviewed.

## Preflight Checklist

- `private.key` exists and is readable only by trusted users.
- `certificate.crt` exists and matches the taxpayer CUIT.
- WSFEv1 is authorized for the taxpayer.
- The point of sale exists and is electronic.
- `confirm_live` is `true` only for intentional live runs.
- The dry-run payload has been reviewed before `--live`.

