# Open AFIP WSFE Skill

Open AFIP WSFE Skill is a publishable Codex skill plus a small Python helper
library for Argentine electronic invoicing through AFIP/ARCA WSAA and WSFEv1.

The project is intentionally dry-run first. A user or agent can build and inspect
the exact `FECAESolicitar` payload without authenticating, opening a network
connection, or issuing a real voucher. Live calls require explicit opt-in.

## What This Is

- A reusable `SKILL.md` for agents that need to prepare AFIP/ARCA WSFEv1 invoices.
- A Python package under `src/open_afip_wsfe/` that validates config and builds WSFE
  payloads.
- A demo CLI that prints a dry-run request by default.
- A secret audit script intended to catch accidental private data before publishing.
- Sanitized examples using only fictional CUITs.

## What This Is Not

- It is not a hosted billing product.
- It is not tax, accounting, or legal advice.
- It does not include real taxpayers, clients, certificates, keys, CAEs, prices,
  private paths, or commercial history.
- It does not call AFIP/ARCA unless you pass `--live` and the config explicitly
  contains `confirm_live: true`.

## Safety defaults

- Examples use fictional CUITs: `20111111112`, `20222222223`, `20333333334`.
- The demo runs in dry-run mode by default.
- Network calls require the `--live` flag.
- Live mode also requires `confirm_live: true` in the config file.
- Certificates and private keys are referenced by user-provided paths and are never
  stored in this repository.
- `scripts/audit_secrets.py` scans for common secret patterns, unexpected CUIT-like
  values, private keys, certificates, CAE-like values, and optional local denylist
  terms.

## Quick start

```bash
python3 scripts/afip_wsfe_demo.py \
  --config examples/config.example.json \
  --request examples/invoice_request.example.json
```

The command prints:

- a short summary
- the WSFE `FECAESolicitar` payload that would be sent

It does not authenticate, query the next voucher number, request a CAE, or call
AFIP/ARCA.

## Repository Layout

```text
.
├── SKILL.md
├── README.md
├── examples/
│   ├── config.example.json
│   └── invoice_request.example.json
├── references/
│   └── afip-codes.md
├── scripts/
│   ├── afip_wsfe_demo.py
│   └── audit_secrets.py
├── src/open_afip_wsfe/
│   ├── payload.py
│   ├── validation.py
│   ├── wsaa.py
│   └── wsfe.py
└── tests/
```

## Using The Skill With An Agent

Point the agent at this repository and ask it to use `SKILL.md`.

Good agent prompt:

```text
Use the open-afip-wsfe skill in this repository to prepare a dry-run Factura A
payload from examples/invoice_request.example.json. Do not call AFIP/ARCA.
```

For branches or forks, keep these invariants:

- dry-run remains the default
- live mode requires two explicit gates: `--live` and `confirm_live: true`
- no real taxpayer, client, certificate, key, CAE, price, path, or commercial data
  is committed
- run the audit before publishing or opening a pull request

## Live mode

Live mode requires optional SOAP dependencies, OpenSSL, and local certificates:

```bash
python3 -m pip install ".[soap]"
python3 scripts/afip_wsfe_demo.py --config path/to/config.json --request path/to/request.json --live
```

Your config must set:

- `environment`: `homologation` or `production`
- `confirm_live`: `true`
- `issuer.cuit`
- `issuer.certificate_path`
- `issuer.private_key_path`

Do not commit live config. Use `config.json` or `*.private.json`; both are ignored.

Production use should be reviewed by a qualified professional. AFIP/ARCA rules and
catalogs can change.

## Secret Audit

Run the audit before publishing:

```bash
python3 scripts/audit_secrets.py .
```

The public audit script intentionally contains no private names. If you need to block
project-specific names or internal paths in your local checkout, create a local file
that is ignored by git:

```text
.audit-secrets.local.txt
```

Add one regular expression per line. Blank lines and lines starting with `#` are
ignored. Example:

```text
# Internal names or paths that must never be published
Some Private Client
internal/path/name
```

You can also pass extra patterns through an environment variable:

```bash
AUDIT_SECRETS_EXTRA_PATTERNS='Private Client|internal/path' \
  python3 scripts/audit_secrets.py .
```

## Development Checks

```bash
python3 -m compileall src scripts tests
python3 -m unittest discover -s tests
python3 scripts/audit_secrets.py .
```

## License

MIT. See `pyproject.toml`.
