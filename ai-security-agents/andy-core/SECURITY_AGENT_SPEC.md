# Andy Security Agent Specification

## Agent identity is not authority

An agent's role description does not grant permissions. All capabilities must be enforced by the orchestrator and tool gateway. Model prompts are not security controls.

## Standard agent contract

Every security agent must declare:
- Stable agent ID and version.
- Division and specialist domain.
- Allowed capabilities and explicit prohibited actions.
- Required input schema and scope requirements.
- Tools it may call, with read/write classification.
- Knowledge-base version and source policy.
- Output schema, evidence requirements, and uncertainty format.
- Evaluation suite and minimum acceptance score.
- Human approval requirements.
- Audit events and failure/stop conditions.

## Red Team contract

Default mode is analysis-only. Lab execution is enabled only when a scope record explicitly identifies the owned/authorised target, permitted test types, time window, exclusions, and approval. The tool gateway must reject requests outside that record. High-risk or state-changing tests require explicit human approval immediately before execution.

## Blue Team contract

Default mode is read-only analysis and recommendation. Changes to firewall rules, IAM, production configuration, endpoint controls, accounts, or data require a human-reviewed change plan and explicit approval. Incident response must preserve evidence and avoid destructive containment without approval unless an organisation has separately configured an approved emergency policy.

## Purple Team contract

May correlate validated Red Team findings with Blue Team controls and propose safe lab tests. It cannot independently declare a vulnerability fixed. Closure requires evidence from a retest and reviewer approval.

## Evidence schema

A finding should contain:
- finding_id, title, domain, affected_asset, affected_version
- scope_id and authorisation reference
- preconditions and reproducibility
- evidence items (type, source, timestamp, hash where appropriate)
- impact, severity, severity rationale
- confidence and confidence rationale
- remediation, validation and retest plan
- reviewer verdict, status, owner, created_at, updated_at

## Stop conditions

Stop and request human review when scope is absent/ambiguous/expired, a test reaches an unexpected system, sensitive third-party data appears, tool output conflicts with scope, destructive impact is possible, or evidence cannot be safely retained.
