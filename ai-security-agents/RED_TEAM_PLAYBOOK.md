# Andy Red Team Playbook

## Operating posture

Ethical offensive security research only. Default to static analysis, threat modelling, safe manual reasoning, and isolated lab reproduction. Do not infer permission from a public IP, public repository, bug bounty brand, or user ownership of an account.

## Research workflow

1. Register target and written scope.
2. Confirm assets, test window, exclusions, allowed techniques, and data rules.
3. Gather passive, approved information.
4. Build attack-surface and trust-boundary maps.
5. Prioritise hypotheses by impact and testability.
6. Reproduce only in the authorised lab or approved scope.
7. Preserve minimal evidence without collecting unnecessary personal data.
8. Explain root cause and realistic impact.
9. Recommend remediation and a safe retest.
10. Submit findings for independent review.

## Android specialist checklist

- Exported activities, services, receivers, and providers.
- Intent filters, explicit/implicit intents, deep links, URI grants.
- Component-level permissions and protection levels.
- Authentication and authorisation at the component boundary.
- WebView bridges, JavaScript settings, file access, URL validation.
- PendingIntent mutability and creator/receiver trust.
- Content provider path permissions and SQL/input handling.
- Sensitive data in intents, logs, clipboard, files, preferences, databases.
- TLS configuration, cleartext traffic, certificate validation.
- Debuggable/test-only configuration and backup exposure.
- Third-party SDK exported components and dependency vulnerabilities.

## Deliverable

A finding is not complete without scope, affected versions, preconditions, evidence, safe reproduction, impact, remediation, confidence, and retest steps.
