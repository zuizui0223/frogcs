# RC4 candidate validation receipt

## Status

**VALIDATED POST-RC3 CANDIDATE**

This receipt does not alter the frozen RC3 release. It records validation of the post-RC3 novelty-maximized candidate on `revision/novelty-evidence-spine-v1`.

## Scientific package

- manuscript: `paper/manuscript_pulse_template_v0_5.md`
- Supporting Information: `paper/supporting_information_pulse_template_v0_3.md`
- title: **Rainfall-associated frog chorus activation reveals recurrent within-taxon multi-site organization**
- numeric synthesis: `revision/INTEGRATED_RESULTS_V0_3.json`
- evidence ledger: `revision/EVIDENCE_CLAIM_LEDGER_V0_1.md`
- evidence hierarchy: `revision/INTEGRATED_EVIDENCE_HIERARCHY_V0_3.md`
- gap/claim map: `revision/PULSE_TEMPLATE_GAP_AND_CLAIM_MAP_V0_4.md`
- literature novelty lock: `revision/TARGETED_LITERATURE_GAP_AUDIT_V0_2.md`
- synthesis/stop rule: `revision/MULTISITE_CHORUS_COHERENCE_SYNTHESIS_V0_2.md`
- figure spec: `revision/FIGURE_REBUILD_SPEC_V0_3.md`

## Claim hierarchy frozen for this candidate

Main text:
1. silence → strong-chorus state switching;
2. excess third-and-later participation within recruited taxa;
3. principal species-response + strictly-prior site-history + dry-persistence comparator;
4. held-out rain × history sensitivity;
5. species-specific historical-site targeting and rain selectivity;
6. taxonomic/geographic breadth with heterogeneity.

SI-only defence/falsification:
- RC11 four-component boundary allocation;
- uniform/persistence-only comparators;
- exact N,K diagnostic;
- raw recurrence percentages;
- route topology;
- FrogID directional consistency;
- trait/context mechanism screens;
- activation-geometry placebo falsification.

## Automated validation

### Manuscript/SI QA

GitHub Actions run: **36808811425**  
Conclusion: **SUCCESS**

Validated:
- title and required claim tokens;
- main/SI routing;
- no legacy overclaim terminology;
- five figure legends;
- manuscript word-count safety;
- abstract ≤350 words;
- keyword count/order;
- exploration/confirmation boundaries.

### Figure rebuild

GitHub Actions run: **36808536220**  
Conclusion: **SUCCESS**

Figure 3 was verified after rebuild to contain only:
- species response + prior site history + dry persistence;
- held-out rain × history gate.

It does not display species-only, uniform-only, persistence-only or exact N,K diagnostics.

### WFTS prospective-code QA

GitHub Actions run: **36818047346**  
Conclusion: **SUCCESS**

The v0.5 real-analysis core supports the prospectively frozen three-way interpretation:
- `replication_support`;
- `informative_nonreplication_of_half_discovery_effect`;
- `inconclusive_nonpass`.

No WFTS response outcome was used to create this rule.

### Anonymous scientific submission bundle

GitHub Actions run: **36818136788**  
Conclusion: **SUCCESS**

All scientific-bundle steps passed:
- integrated manuscript QA;
- figure rendering;
- metadata smoke test;
- anonymous manuscript and SI DOCX build;
- JAE formatting/anonymity validation;
- bundle assembly;
- artifact upload.

Artifact:
- name: `frogcs-jae-pulse-template-scientific-submission`
- ID: `11142765331`
- size: 776,911 bytes
- digest: `sha256:0cca77c00284a288fc800af81dd3bb8ef5050038e59d79d45fbbbd8eb36c506a`

## Inferential boundary

This remains a post-opening synthesis within NAAMP. The stronger novelty framing does not convert the multi-site result into a preregistered discovery. Prospective external confirmation remains unresolved until an eligible external dataset is run under the frozen authority.

## Release rule

This candidate may be promoted to RC4 only without changing scientific endpoints, main/SI routing, principal comparator, title-level novelty claim or WFTS interpretation rule. Copy-edit-only changes remain permissible if they do not change meaning.
