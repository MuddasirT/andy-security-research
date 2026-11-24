# Andy Security Divisions

## Mission

Build a governed, evidence-driven security organisation with three cooperating divisions: Red Team, Blue Team, and Purple Team. These are role definitions and operating plans; they do not imply autonomous workers or tools exist until implemented, tested, and deployed.

## 1. Andy Red Team: Offensive Security Research

**Mission:** Find and explain security weaknesses in systems the owner controls, intentionally vulnerable labs, or targets explicitly covered by written authorisation and program scope.

### Specialist cells
- **Web Application Assessment:** OWASP Web/API risks, authentication, sessions, access control, input handling, business logic.
- **Android and Mobile Assessment:** exported components, intents, deep links, WebViews, storage, cryptography use, network security config, IPC, SDK/library risks.
- **API and Identity Assessment:** OAuth/OIDC configuration, token handling, authorisation boundaries, rate limiting, object-level access.
- **Cloud and Infrastructure Assessment:** IAM policy review, exposed services, network segmentation, secrets handling, secure configuration.
- **Vulnerability Research:** CVE/CWE analysis, affected-version validation, root-cause analysis, safe lab reproduction.
- **Exploit Validation Engineer:** create minimal reproducible proofs in isolated labs; document prerequisites, impact, and cleanup.
- **Adversarial Test Planner:** turn threat models into scoped, non-destructive test plans.

### Required output
Each finding must include scope and authorisation, asset/version, preconditions, reproducible lab steps, observed evidence, impact, severity rationale, remediation, retest procedure, and limitations.

### Hard boundaries
- No scanning, exploitation, credential testing, persistence, exfiltration, or social engineering against third-party targets without explicit authorisation and scope.
- No destructive testing or uncontrolled payloads.
- Use synthetic data and isolated environments by default.
- Stop when scope is unclear, authorisation expires, or unexpected access to real user data occurs.
- Do not provide stealth, evasion, persistence, or malware deployment functionality.

## 2. Andy Blue Team: Defensive Security and Resilience

**Mission:** Prevent, detect, investigate, contain, and recover from security incidents.

### Specialist cells
- **Security Architecture:** threat modelling, trust boundaries, secure design reviews, defence in depth.
- **Application Security Engineering:** secure coding, code review, dependency and secrets review, security requirements.
- **Detection Engineering:** detection logic, telemetry design, alert quality, false-positive tuning.
- **Incident Response:** triage, evidence preservation, containment plans, recovery and post-incident review.
- **Threat Intelligence:** track public advisories, CVEs, attacker techniques, indicators with provenance and confidence.
- **Cloud and Endpoint Hardening:** least privilege, configuration baselines, patching, logging, backup and recovery.
- **Android Defence:** manifest hardening, component permissions, secure storage, network policy, Play Integrity considerations, privacy-safe telemetry.
- **Security Governance:** risk register, control mapping, audit trails, exceptions and remediation ownership.

### Required output
Defensive recommendations must state the threat addressed, control objective, implementation steps, validation method, operational cost, residual risk, and evidence.

## 3. Andy Purple Team: Validation and Improvement

**Mission:** Connect offensive findings to defensive controls without allowing either side to grade itself.

### Responsibilities
- Map Red Team findings to defensive controls and detection opportunities.
- Create safe test cases for owned lab systems.
- Verify whether Blue Team controls prevent or detect the simulated behaviour.
- Record gaps, false positives, false negatives, and remediation status.
- Require retesting before closing high-risk findings.

## Shared research and quality standards

Every division uses:
- Versioned specialist knowledge bases with source, publisher, publication/retrieval date, and confidence.
- Task-scoped permissions and explicit tool allowlists.
- Reproducible test plans and structured evidence records.
- Independent review for high-impact findings.
- Evaluation suites, regression tests, and agent version history.
- Human approval gates for any action that changes systems or touches sensitive data.

## Severity and confidence

Keep severity (impact/risk) separate from confidence (strength of evidence). Never inflate confidence because a model sounds certain. Unknowns remain explicit.

## Build sequence

1. Secure core: permissions, audit log, scope registry, evidence schema, safe tool boundary.
2. Red Team foundation: Android and web lab assessment specialists with no arbitrary target execution.
3. Blue Team foundation: architecture review, secure-code review, and remediation specialists.
4. Purple Team: finding-to-control mapping and safe regression validation.
5. Add approved scanners and lab tools only after threat modelling, allowlisting, dry-run, output validation, and human approval.
6. Add more specialist cells only when evaluation results justify them.
