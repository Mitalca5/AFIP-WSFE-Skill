# Open AFIP WSFE Skill

Skill and helper library for AFIP/ARCA electronic invoicing through WSAA and WSFEv1.

This repository is designed for publication. It contains no real taxpayers, clients,
certificates, keys, CAEs, prices, private paths, or commercial data. All examples use
fictional CUITs.

## Safety defaults

- Examples run in dry-run mode by default.
- Network calls require explicit `--live`.
- Live mode refuses to run unless `confirm_live: true` is present in config.
- Certificates and private keys are loaded from user-provided paths and are never
  committed.
- `scripts/audit_secrets.py` scans the repository for common secret and business-data
  patterns before publishing.

## Quick start

```bash
python scripts/afip_wsfe_demo.py \
  --config examples/config.example.json \
  --request examples/invoice_request.example.json
```

The command prints the WSFE request payload that would be sent to AFIP. It does not
authenticate or call AFIP unless `--live` is passed.

## Live mode

Live mode requires optional SOAP dependencies and local certificates:

```bash
python -m pip install ".[soap]"
python scripts/afip_wsfe_demo.py --config path/to/config.json --request path/to/request.json --live
```

Your config must set:

- `environment`: `homologation` or `production`
- `confirm_live`: `true`
- `issuer.cuit`
- `issuer.certificate_path`
- `issuer.private_key_path`

Production use should be reviewed by a qualified professional. AFIP/ARCA rules and
catalogs can change.

## Development checks

```bash
python -m compileall src scripts tests
python -m unittest discover -s tests
python scripts/audit_secrets.py .
```

