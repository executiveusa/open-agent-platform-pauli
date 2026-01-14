# Relay Loop

The Relay Loop uses GitHub Actions as the event bus. Issues labeled `relay:run` are picked up, planned, implemented, verified, reviewed, and merged according to the policy engine.

## Labels
- relay:run
- relay:planned
- relay:pr
- relay:safe
- relay:blocked
- relay:heal
- relay:merged
- autonomy:fuck_it

## Policy
Risk tiers and allowlists are enforced by `/tools/relay_policy.py`.
