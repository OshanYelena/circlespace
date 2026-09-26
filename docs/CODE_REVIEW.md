# Code review and merge policy

## Automated pull request gates

Every pull request runs three required status checks:

- **Architecture** rejects imports outside the declared backend dependency map and direct frontend HTTP calls outside the shared API client.
- **Backend** enforces Ruff formatting/lint and a test coverage floor of 75%.
- **Frontend** enforces ESLint, strict TypeScript, unit tests, and a production Next.js build.

Feature routers may consume the auth module's public dependency aliases. Other cross-module dependencies must be added deliberately to the allowlist in `scripts/check_architecture.py` and justified in the pull request.

Dependabot opens grouped weekly dependency updates, which pass through the same review pipeline.

## GitHub branch protection

Configure a ruleset targeting `main` with these settings after the repository is published:

1. Require a pull request before merging.
2. Require at least one approving review and dismiss stale approvals.
3. Require review from Code Owners.
4. Require the `Architecture`, `Backend`, and `Frontend` checks.
5. Require branches to be up to date before merging.
6. Block force pushes and branch deletion.
7. Require conversation resolution.
8. Apply the ruleset to administrators as well.

Use squash merging so each pull request becomes one coherent change in `main`. Emergency bypass should be restricted to repository administrators and recorded in the pull request.

## Human review order

1. Confirm the requested behavior and authorization model.
2. Review module ownership and data flow before implementation details.
3. Inspect persistence constraints and migration reversibility.
4. Review API contracts and failure behavior.
5. Review UI states and accessibility.
6. Confirm tests exercise business behavior rather than implementation details.
