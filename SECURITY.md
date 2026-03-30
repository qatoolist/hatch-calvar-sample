# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| Latest release | Yes |
| Older releases | No |

Only the most recent CalVer release receives security updates.

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it by opening an issue on GitHub:

**https://github.com/QAToolist/hatch-calvar-sample/issues**

When reporting, please include:

- A description of the vulnerability
- Steps to reproduce the issue
- The potential impact
- Suggested fix (if any)

We will acknowledge receipt of your report within 48 hours and aim to provide a fix or mitigation plan within 7 days for confirmed issues.

## Scope

This is a sample/template project with no runtime dependencies. Security concerns are most likely to involve:

- CI/CD workflow configuration (GitHub Actions)
- Dependency supply chain (dev dependencies)
- Code injection via version string handling

## Security Tooling

This project uses the following security tools as part of its CI pipeline:

- **Bandit** -- static analysis for common Python security issues
- **pip-audit** -- checks installed packages against known vulnerability databases
- **Safety** -- scans dependencies for published CVEs
- **detect-private-key** -- pre-commit hook to prevent accidental key commits
- **gitleaks** -- optional secret scanning (if installed locally)

Run security checks locally:

```bash
make security
```
