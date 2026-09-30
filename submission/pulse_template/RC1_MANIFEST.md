# Integrated release candidate RC1

**Scientific release branch:** `release/jae-higher-order-rc1`  
**Submission candidate branch:** `submission/jae-higher-order-v1`  
**Frozen RC1 commit:** `c5d40b6302c8166e965b213757328501de685fb9`

At creation, both refs were byte-identical to:

`revision/pulse-template-synthesis-v1`

and were created only after both:

- `pulse-template manuscript QA`
- `pulse-template submission pipeline`

had passed on the validated scientific package.

## Scientific authority

RC1 freezes:

- `paper/manuscript_pulse_template_v0_3.md`
- `paper/supporting_information_pulse_template_v0_1.md`
- canonical five-figure set in `figures_pulse_template/`
- `revision/INTEGRATED_RESULTS_V0_1.json`
- `revision/PULSE_TEMPLATE_GAP_AND_CLAIM_MAP_V0_2.md`
- `revision/HIGHER_ORDER_CHORUS_COHERENCE_SYNTHESIS_V0_2.md`
- integrated cover letter and submission templates under `submission/pulse_template/`

## Scientific stop

RC1 does not authorize new same-data mechanism exploration. Scientific changes require a new release candidate rather than silently moving RC1.

Allowed on the revision track:

- copy-editing;
- formatting;
- submission metadata;
- archive tooling;
- genuinely external replication.

## Original submission authority

The earlier frozen boundary-allocation submission remains separately preserved on `main` and its release/submission branches. RC1 does not overwrite that history.


## Validated anonymous bundle for RC1

Workflow run: `36743103276`  
Artifact: `frogcs-jae-pulse-template-scientific-submission`  
Artifact ID: `11111850829`  
Artifact size: **679,822 bytes**  
Artifact digest: `sha256:d0d9563ef8f54a1eca80d86b513eb7860d249d1e870bbec0f17bf5f8452ea38f`

The workflow run reports the frozen source head as:

`c5d40b6302c8166e965b213757328501de685fb9`

At the time this manifest was updated, the revision track was **3 commit(s) ahead** of RC1 and RC1 remained unchanged. Those later revision-only commits add archive tooling/documentation rather than alter RC1.
