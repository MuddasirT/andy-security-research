# Andy Security Research

A practical learning and research workspace for ethical application security, Android security, web security, and AI-assisted security engineering.

## Mission

Build the skills to identify, validate, document, and responsibly disclose security weaknesses in systems that we own or are explicitly authorised to test.

## Research tracks

- **Web application security:** HTTP, authentication, access control, OWASP Top 10, API security, and business-logic testing.
- **Android application security:** APK structure, app components, permissions, data storage, network security, reverse engineering, and runtime analysis.
- **AI-assisted security research:** LLM-supported code review, evidence triage, research workflows, and carefully bounded agents with human approval.

## Working principles

1. Test only systems that are owned by us or explicitly in scope and authorised.
2. Use local intentionally vulnerable applications for hands-on practice.
3. Keep testing safe and proportionate. Avoid disruption, data access beyond the test account, persistence, or uncontrolled automation.
4. Treat AI-generated findings as hypotheses until independently verified.
5. Record reproducible evidence, impact, limitations, and remediation.
6. Follow each programme's scope, rules, and disclosure process.

## Planned workspace

As the programme grows, research notes and practical work will be organised into:

- `foundations/` — networking, HTTP, Linux, and security fundamentals
- `web-security/` — web and API security notes and lab exercises
- `android-security/` — mobile testing notes and Android lab work
- `ai-security-agents/` — safe AI-assisted workflows and experiments
- `reports/` — responsible disclosure report templates and sanitised examples
- `resources/` — references, checklists, and tool documentation

Directories will be added when they contain useful material.

## Learning status

**Academy status: Paused.** This repository is initialised, but no course day or practical assessment has been started or marked complete.

## Evidence note template

For each future finding, record:

- Target and explicit authorisation/scope
- Environment and date
- Preconditions and test account
- Reproduction steps
- Expected versus observed behaviour
- Evidence with secrets and personal data removed
- Security impact and severity rationale
- Suggested remediation
- Retest result

## Disclaimer

This repository is for education and authorised security research only. It is not permission to test any third-party system. Always obtain explicit authorisation and follow the applicable rules of engagement.
