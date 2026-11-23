# Lab 01: BOLA / IDOR in a Demo Payment API

**Status:** Practical exercise completed  
**Environment:** Local FastAPI application on the researcher's Mac  
**Validation:** 4 automated tests passed

## Objective

Understand and reproduce Broken Object Level Authorization (BOLA), also commonly discussed as Insecure Direct Object Reference (IDOR), in a deliberately vulnerable local API. Then implement an authorization check and verify the fix with regression tests.

## Scope and safety

This exercise used a locally hosted, intentionally vulnerable FastAPI application and fictional users with dummy data. No third-party systems or real user data were involved.

The `X-User-ID` header is a teaching simulation only. It is not secure authentication: a real client can forge it. Production systems must establish identity from a validated server-side session or cryptographically verified token, then enforce authorization on every requested object.

## Lab scenario

Two fictional users were created:

- Alice: user ID `101`
- Bob: user ID `202`

The endpoint was:

```http
GET /api/users/{user_id}/profile
```

The client supplied the simulated identity using `X-User-ID`.

## Vulnerability and root cause

The vulnerable implementation checked that the requesting user ID existed and that the requested profile ID existed, but did not verify that the requester was permitted to access that profile.

Alice could therefore request Bob's profile by changing the object identifier from `101` to `202`.

**Observed result:** Both Alice's own-profile request and Alice's request for Bob's profile returned profile data.

**Root cause:** Missing object-level authorization. Authentication or the existence of an object does not establish permission to access it.

## Classification

- **OWASP API Security Top 10 (2023):** API1:2023 Broken Object Level Authorization.
- **CWE-639:** Authorization Bypass Through User-Controlled Key, where the weakness involves bypass through a user-controlled key. This is a relevant mapping for this lab scenario; CWE mapping should be selected based on the exact implementation and root cause.

BOLA is the broader API security category. IDOR is a commonly used term for a related direct-reference pattern.

## Remediation implemented

The lab endpoint added a server-side ownership check before returning the profile:

```python
if x_user_id != user_id:
    raise HTTPException(
        status_code=403,
        detail="Access forbidden"
    )
```

This equality check is deliberately simple for a two-user teaching lab. Real applications should use authorization policies that account for ownership, roles, tenant boundaries, delegated access, and other business rules. The trusted identity must come from validated authentication, never from an arbitrary client-controlled header.

## Automated verification

A pytest suite was created with four checks:

| Test | Expected result | Observed result |
|---|---:|---|
| Alice accesses Alice's profile | 200 | PASSED |
| Alice attempts to access Bob's profile | 403 | PASSED |
| Bob accesses Bob's profile | 200 | PASSED |
| Unknown identity attempts access | 401 | PASSED |

**Researcher-reported result:** 4 tests passed.

Run the suite locally with:

```bash
pytest -v
```

## Key lessons

1. Authentication answers who the requester is; authorization determines what that requester may do.
2. Never trust object identifiers supplied by the client as proof of permission.
3. Enforce object-level authorization on the server for every access path.
4. Test both permitted and denied access paths.
5. Keep regression tests so authorization failures are less likely to return.

## Limitations

- The lab uses an in-memory dictionary rather than a database.
- The identity header is not real authentication.
- The equality-based ownership rule is not a complete authorization model.
- No production deployment, token validation, multi-tenant policy, or role-based access control was tested.

## Next research steps

- Replace the simulated identity header with a locally validated authentication mechanism.
- Add tests for cross-tenant access and role-based permissions.
- Review authorization coverage across read, update, delete, and nested-resource endpoints.
- Add automated negative tests for every protected object operation.

## References

- OWASP API Security: API1:2023 Broken Object Level Authorization — https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/
- MITRE CWE-639 — https://cwe.mitre.org/data/definitions/639.html
