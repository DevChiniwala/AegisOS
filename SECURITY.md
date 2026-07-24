# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously. If you discover a vulnerability in AegisOS, please report it responsibly.

**DO NOT** open a public GitHub issue for security vulnerabilities.

### How to Report

1. Email: security@aegisos.dev (or open a private security advisory on GitHub)
2. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- Acknowledgment within 48 hours
- Status update within 7 days
- Fix timeline depends on severity:
  - Critical: 24-72 hours
  - High: 1-2 weeks
  - Medium: 1 month
  - Low: Next release

### Scope

The following are in scope:
- AegisOS API and core services
- Authentication and authorization
- Data encryption and key management
- Agent execution sandboxing
- Graph query injection
- SDK and CLI tools

### Out of Scope

- Issues in third-party dependencies (report upstream)
- Social engineering attacks
- Denial of service attacks against development instances

## Security Features

AegisOS implements:
- AST-based safe expression evaluation (no eval())
- HKDF key derivation for encryption
- JWT with JTI claims and token revocation
- Cypher injection prevention (enum whitelist + regex validation)
- Input validation at all API boundaries
- Secrets detection in CI pipeline (bandit + detect-secrets)
