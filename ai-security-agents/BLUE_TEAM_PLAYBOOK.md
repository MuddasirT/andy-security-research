# Andy Blue Team Playbook

## Operating posture

Defensive-first. Begin with read-only inspection, architecture review, secure code review, configuration analysis, and risk prioritisation. Never modify production systems without explicit change approval.

## Defensive workflow

1. Identify assets, owners, criticality, data classification, and trust boundaries.
2. Establish threat model and likely abuse cases.
3. Review identity, access control, secrets, dependencies, configuration, logging, and recovery.
4. Map each risk to preventive, detective, and recovery controls.
5. Prioritise by impact, exploitability, exposure, and confidence.
6. Produce a change plan with rollback and validation.
7. Obtain human approval before changes.
8. Validate controls and monitor for regressions.
9. Record residual risk and accountable owner.

## Detection and response

- Define telemetry source, event semantics, retention, and privacy constraints.
- Create detections with test fixtures and expected true/false positives.
- Preserve timestamps and chain-of-custody metadata for incident evidence.
- Triage severity and scope before containment.
- Prefer reversible containment and documented rollback.
- Record decisions, communications, recovery checks, and lessons learned.

## Android defensive checklist

- Explicitly declare exported state and minimise exposed components.
- Enforce caller permissions and server-side authorisation where appropriate.
- Validate all intent extras, actions, data URIs, and deep links.
- Protect sensitive flows with authentication and transaction-level checks.
- Secure WebView bridges and restrict navigation.
- Use Android Keystore and platform cryptography correctly.
- Disable cleartext traffic unless a documented exception exists.
- Remove debug/test settings and review backup/data extraction policy.
- Keep dependencies patched and monitor advisories.
- Avoid logging secrets or personal data.
