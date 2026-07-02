---
name: open-afip-wsfe
description: "Prepare and optionally emit Argentine AFIP/ARCA WSFEv1 electronic invoices and credit/debit notes using sanitized config-driven workflows. Use when Codex needs to build, validate, dry-run, audit, or execute WSAA/WSFEv1 invoicing flows for Argentina without embedding private taxpayer, client, certificate, key, CAE, price, or commercial data."
---

# Open AFIP WSFE

Use this skill to prepare AFIP/ARCA WSFEv1 electronic invoice payloads, validate
configuration, and run dry-run demos. Treat live issuance as a high-impact action.

## Core Rules

- Default to dry-run. Do not call AFIP/ARCA unless the user explicitly requests live mode.
- Require `--live` and `confirm_live: true` before any network call.
- Never invent or persist real CUITs, names, client data, certificates, keys, CAEs,
  prices, private paths, or commercial history.
- Use fictional examples only: `20111111112`, `20222222223`, `20333333334`.
- Keep credentials outside the repository. Certificate and key paths belong in private
  local config files ignored by git.
- Run the secret audit before publishing, committing, or sharing changes.

## Workflow

1. Read the user's config and invoice request.
2. Validate CUIT shape, voucher type, IVA condition, concept dates, and totals.
3. Build a WSFE `FECAESolicitar` payload in dry-run mode.
4. If live mode is explicitly requested, verify `confirm_live: true`, obtain WSAA token
   and sign, query the next voucher number, and call WSFEv1.
5. Report CAE, CAE expiration, voucher number, observations, and errors without storing
   sensitive response data in the repository.

## Live Issuance

Use `scripts/afip_wsfe_demo.py --live` only after a dry-run review. A live request:

1. Signs a WSAA login ticket with the user's private certificate and key.
2. Calls WSAA `loginCms`.
3. Calls WSFEv1 `FECompUltimoAutorizado`.
4. Calls WSFEv1 `FECAESolicitar`.

Require all of these before live mode:

- explicit user request to issue
- `--live`
- `confirm_live: true`
- private config outside the repository
- valid `issuer.certificate_path` and `issuer.private_key_path`
- reviewed amount, dates, receiver CUIT, voucher type, and point of sale

Command pattern:

```bash
python3 scripts/afip_wsfe_demo.py \
  --config path/to/config.private.json \
  --request path/to/invoice_request.private.json \
  --live
```

## Bundled Resources

- `scripts/afip_wsfe_demo.py`: CLI for dry-run payload generation and explicit live calls.
- `scripts/audit_secrets.py`: repository scanner for private data and secret patterns.
- `examples/config.example.json`: sanitized issuer configuration.
- `examples/invoice_request.example.json`: sanitized invoice request.
- `references/afip-codes.md`: common WSFE code tables.

## Validation Commands

Run these before handoff:

```bash
python -m compileall src scripts tests
python -m unittest discover -s tests
python scripts/audit_secrets.py .
```
