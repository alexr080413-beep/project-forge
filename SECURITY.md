# Security

Project Forge does not yet have production runtime behavior, deployed services, or published packages.

## Reporting

Until a formal disclosure process is established, report suspected vulnerabilities privately to the project maintainers.

## Handling Sensitive Data

- Do not commit secrets, credentials, private keys, or tokens.
- Use local environment files for machine-specific values.
- Keep generated outputs that may contain sensitive information out of Git.
- Treat files in `outputs/` as local artifacts unless explicitly reviewed for publication.
