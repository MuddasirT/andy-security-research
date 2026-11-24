# Andy Agentic Security Lab Architecture

## Goal

Andy should accept a security objective, identify the technology and assets involved,
select the appropriate specialist playbooks, coordinate Red/Blue/Purple work, and
produce an evidence-backed remediation and retest record.

The architecture is platform-neutral. Domain packs can cover web applications,
Android, iOS, Flutter, APIs, identity, backend, cloud, infrastructure, desktop,
networks, hardware, IoT, embedded systems, and future technologies.

## Target workflow

1. **Intake and classification**
   - Parse the objective and identify candidate platforms, versions, assets, and trust boundaries.
   - Ask for missing facts that materially affect safety or test accuracy.
   - Separate user-supplied facts from assumptions and model inferences.
2. **Scope and authorisation**
   - Resolve the exact target, owner, permitted operations, exclusions, time window, and approval.
   - Refuse execution if scope is absent, ambiguous, expired, or mismatched.
   - Scope registration is not proof of ownership and is not itself an execution grant.
3. **Red Team planning**
   - Select domain-specific attack-surface checklists and safe test procedures.
   - Produce a test plan with preconditions, expected results, risk, evidence requirements, and stop conditions.
   - Require human approval before active or state-changing validation.
4. **Controlled discovery and validation**
   - Execute only tools exposed through the policy-enforcing tool gateway.
   - Begin with read-only inventory, static analysis, dependency/configuration checks, and passive evidence.
   - Run active checks only when the exact operation is in the approved scope.
   - Preserve command, tool version, target, timestamp, output, and evidence hashes.
5. **Blue Team response**
   - Map validated findings to preventive controls, detection, hardening, and remediation.
   - Produce a change plan, impact analysis, backup/rollback plan, and verification steps.
   - Production writes and consequential changes require explicit human approval.
6. **Purple Team validation**
   - Retest in the same authorised scope.
   - Compare expected and observed prevention/detection.
   - Close findings only with retest evidence and independent review.
7. **Quality and audit**
   - Validate report schema, evidence references, source provenance, technical accuracy, severity, and completeness.
   - Persist immutable audit events and retain unresolved disagreements.

## Tool gateway: mandatory security boundary

No specialist prompt or model output grants tool permission. Every tool adapter must
request authorisation from a central gateway immediately before execution.

The gateway must enforce:
- Exact target and operation matching; no implicit wildcards.
- Active time window and explicit exclusions.
- Per-agent tool allowlists and least privilege.
- Human approval for active scans, exploit validation, writes, and consequential actions.
- Rate, concurrency, request-volume, and time limits.
- Egress restrictions and lab network isolation where possible.
- Full audit records and safe cancellation.
- Fail-closed behaviour when policy, scope, or tool state cannot be verified.

A stored approval reference is an audit field, not a cryptographic or identity proof.
The future approval workflow must capture an explicit owner action and bind it to
the exact target, operations, time window, and plan digest. Do not trust a model-
generated approval reference or a sentence inside a task description.

## Safe capability progression

### Stage A: analysis-only
Current Red, Blue, and Purple specialists reason over supplied material. They have
no shell, browser, network, repository, device, scanner, or exploitation tools.

### Stage B: read-only lab tooling
Add narrowly scoped adapters for local artifact inspection, source/static analysis,
dependency and configuration review, and read-only cloud inventory. Each adapter
must be tested against gateway denial cases before it can be registered.

### Stage C: controlled active validation
Add bounded web/API/mobile/cloud test adapters for isolated labs and explicitly
authorised scopes. Each operation must be individually allowlisted and approved.
No stealth, persistence, malware deployment, credential theft, destructive testing,
or uncontrolled public-target scanning.

### Stage D: defensive changes
Blue Team can generate and validate remediation proposals. Applying production
changes remains a human-approved workflow with rollback and post-change checks.

### Stage E: multi-domain agentic coordination
Introduce specialist domain packs, task decomposition, bounded delegation,
independent review, retries, cancellation, budgets, and agent evaluations. Agents
must not recursively create unlimited work or expand their own permissions.

## Immediate implementation sequence

1. Integrate the universal quality gate into orchestration and task persistence.
2. [x] Build a fail-closed policy-enforcing tool gateway around the existing authorisation registry.
3. Add an explicit owner approval workflow and scope-to-task binding.
4. Add a local, read-only artifact analysis adapter and a deliberately vulnerable lab fixture.
5. Add web/API static and read-only discovery packs, then mobile and cloud packs.
6. Add individually approved active validation adapters and audit evidence capture.
7. Add Blue remediation plans and Purple retest/closure workflow.
8. Add technical accuracy evaluations and cross-team correlation.

## Current reality

The existing six agents are analysis workers, not autonomous tool operators. The
SQLite authorisation registry and a fail-closed tool gateway core now exist, but
the gateway is not yet integrated into the orchestrator and no scanner or
exploitation adapters are registered. The gateway requires a caller-supplied
approval checker for active and state-changing operations; the concrete owner
approval workflow and scope-to-task binding remain future work. The current
quality gate validates report shape and evidence references; it does not prove
factual correctness, source authenticity, or vulnerability exploitability.
Do not describe later stages as implemented until they are built and tested.
