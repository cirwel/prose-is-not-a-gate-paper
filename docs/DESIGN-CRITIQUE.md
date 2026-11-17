# Pre-Implementation Design Critique & Dispositions

**Consultation:** `unitares-governance:consult(purpose="critique", privacy="cloud_allowed", host_id="claude:host-adapter")`
**Consultation ID:** `d2e9d95b-f160-40db-b03e-d7ff3f421e87`
**Recorded:** `2026-11-17T06:15:22Z` (`anthropic`, thorough effort)

## Critique Findings & Architectural Dispositions

1. **Ticket Availability & Information Floors (`silent_partial` Detectability):**
   - *Critique:* Withholding the engineering ticket in `discretion` or `goal_duty` would create an unwinnable information floor rather than measuring prose-induced miscalibration. Also pre-specify the release rule for `disclosed_partial`.
   - *Disposition:* Every primary arm (`Exp A`, `Exp B`, `Exp C`) renders the full 2-requirement engineering ticket explicitly (`Req 1` and `Req 2`), plus a dedicated `no_ticket_control` arm in `Exp B` to establish the missing-request baseline. Prompts state an explicit release policy: merge *only* if complete and passing; hold incomplete (`disclosed_partial`, `silent_partial`) or failing (`false_ci`) PRs. Report a per-cell oracle ceiling.

2. **Exp C Gate Alignment & Deterministic Header Isolation (`ungated` vs. `gated`):**
   - *Critique:* Suppressing `1-of-3` dissents whenever `pytest` passes would swallow valid solitary catches on `silent_partial`, and adding a deterministic `pytest`/diff header only to `gated_crux_brief` would confound enforcement with extra information.
   - *Disposition:* All three `Exp C` multi-family brief arms (`consensus_brief`, `ungated_crux_brief`, `gated_crux_brief`) share the **exact same deterministic `pytest` + `git diff --stat` header** above the neutral 3-section brief. `gated_crux_brief` clears `cruxes`/`unverified_premises` when deterministic `pytest` passes and Stage 1 is unanimously `approve`, or drops solitary `1-of-3` holds that assert only test failure contradicting deterministic `pytest == 0` without naming a missing ticket requirement—preserving requirement-omission dissents.

3. **Matched `PR Metadata:` Slot, Realistic Badges, & Signal Detection Metrics:**
   - *Critique:* Varying length/position across signal arms confounds salience with semantics, and `"Commit/Attestation: ✔ Verified"` combines signals artificially; `ci_mismatch_prose` is negative evidence and should be analyzed separately.
   - *Disposition:* Render every metadata arm inside an identical fixed-position `PR Metadata:` slot with a length-matched `neutral` baseline and GitHub/Sigstore-style phrasing (`badge_verified`, `sig`, `scoped_verified`), analyze `ci_mismatch_prose` strictly on `false_ci` override behavior, and report Signal Detection metrics (`hit_rate`, `false_alarm_rate`, `Net J`, `d'`, `criterion c`) alongside exact repo-level paired tests.

4. **Statistical Power, Calibration Split, & Worker Obstacle Design:**
   - *Critique:* `N = 24` detects only ~35–40 pp swings per contrast, repeated seeds cannot inflate `N`, and `Part 2` requires feasible-but-tricky `Req B` implementations plus test-tampering logging.
   - *Disposition:* Construct `N = 36` confirmatory repositories (`T00..T35` across 12 engineering domains, counterbalanced `18` `Req 1` / `18` `Req 2` omissions) cleanly separated from `4` calibration repositories (`C00..C03`). Score each repository as an independent unit (`T00..T35`), lock <=3 confirmatory contrasts per hypothesis family with Holm correction, prove solvability of all `40` repos via verified `patch_clean` reference solutions, require structured worker `unimplemented_requirements` reporting, and detect test tampering via AST comparison against `base_files`.
