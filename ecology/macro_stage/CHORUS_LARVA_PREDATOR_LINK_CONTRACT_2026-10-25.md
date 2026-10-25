# Direct same-pond chorus → larval cohort → aquatic enemy phenology
2026-10-25. Design fixed after source metadata audit, before first joint time-series outcome computation. New exploratory ecological research; JAE RC6 main untouched.

## Verified original sources
1. Carter, Saenz & Rudolf (2018), original 2001–2015 daily male calling workbook, Dryad DOI 10.5061/dryad.84fq2vh, archived version 26703, original 14,777,689 bytes and MD5 37dd4dc8289f0c1ce8d249791b3df558. Eight Texas forest ponds and 12 species. No egg-laying, metamorph or breeding success inferred from adult calling.
2. Carroll, Saenz & Rudolf (2023), original weekly aquatic funnel trap workbook, Dryad DOI 10.25338/B8G92P, archived version 218704, original 196,918-byte SHA256 302f1d976725ff926c682331a34e302262adbdb3be1f80fc67c1ccc990343f6f; verified original README SHA256 d2729af5cf0e685b15a26fc80f9ce589010c67e3cda545c9b2160c6b8906a5ff. Eight pond sheets, 296 weekly rows/pond, 11 species tadpoles, and aquatic insects/other amphibians/fish.
3. The frog larval code Naiad refers to dragonfly larvae according to the verified original README. Mole.sala.larvae refers to Ambystoma talpoideum larvae. Fish columns are juvenile smallmouth bass and green sunfish. These are trap catches, NOT predation events.

## New ecological estimands
- For each verified identical pond × frog species × year, map adult nightly calling to weekly bins preserving total calling activity, and larval weekly trap counts to the original source weeks.
- Compute first positive calling date and first positive tadpole capture date and their elapsed days. Their relationship is reproductive ACOUSTIC expression to larval detection, not egg laying or reproduction success. Record date missingness and left-censoring.
- Use species-specific count-weighted mean/median calling date and larva-capture date as a timing sensitivity, not a substitute for a real egg-laying observation.
- Within pond×year (2002–2006 full-year primary), define frog larva and dragonfly naiad positive weeks and same-week positive overlap, with exact fixed-pond-year marginal and circular-shift controls; partner salamander larvae, water beetles and fish are separate descriptive guilds.
- Investigate whether dragonfly encounter windows occur disproportionately in weeks after a frog chorus rise when species-specific larval availability is observed; year/pond blocking, avoid independent weekly row pseudo-replicates, no post-hoc lag optimization.

## Critical habitat limitations
- Existing tadpole and daily calls workbooks DO NOT contain quantified aquatic vegetation cover, within-pond microhabitat hydroperiod, water depth or canopy measurements. Forest site complex, pond size/depth and fish are partly aliased and cannot represent a causal vegetation-treatment variable.
- Original tadpole dates include one 2001-03-31 serial date embedded among March 2004 rows. Respect original dates, do not silently correct; primary full-year lag/overlap window 2002–2006. Year 2001 only sensitivity due incomplete start.
- Source pond labels in the two files must be explicitly mapped/verified; never join if identity uncertain. No adult calling record has yet been ingested for this new study at the moment this plan is written.

## Biological falsification
A broad chorus that is followed by tadpole detections but no dragonfly larval co-capture is a different ecological pathway from one followed by co-captured dragonfly larvae or Ambystoma larvae. Both are potential encounters; neither indicates mortality without directly measured attacks/survival. The macro GBIF stage-window project gives geographic availability context, NOT same-pond predation proof.

## Source originality & publication status
This is a new reanalysis of older published data and is exploratory, not a new field experiment nor independent confirmation of the Carter/Carroll phenology studies. A high-impact trophic mechanism claim requires measured attack, offspring survival, or an independent experimental manipulation of predator-stage timing.
