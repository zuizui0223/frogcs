# NPS GLKN source preflight size/field correction v0.2 — 2026-10-22

This modifies **retrieval scope only**, before any NPS acoustic detection values have been examined. Original contract `exploration/NPS_GLKN_FROG_INDEPENDENT_SOURCE_ONLY_CONTRACT_V0_1.md` remains authoritative for ecological inference boundaries and named taxa.

## Prior failure and source-only diagnostic

[Original response-blind workflow 39721668368](https://github.com/zuizui0223/frogcs/actions/runs/39721668368): 60 MB per-file cap stopped downloading both NPS official CSVs **before any frog response readback**. NPS XML metadata download succeeded; **131,226 bytes**, SHA256 **a37af87cd333168f52503f823041c4ab578b6968333c7d5f315604222ae4eb8f**.

[Response-blind HTTP HEAD/first 1024 bytes probe 39721873226](https://github.com/zuizui0223/frogcs/actions/runs/39721873226) authenticated no scientific observations:
- NPS DataStore reference **2320505**;
- official frog audio-annotation CSV asset **763377**, **68,581,307 bytes**, HEAD 200 / byte-range 206;
- official hourly temperature CSV asset **763378**, **282,010,401 bytes**, HEAD 200 / byte-range 206;
- NPS official metadata XML **763466**, **131,226 bytes**.
- Frog CSV header, in original order:
`FileName,ParkCode,SiteLocation,StartTime,EventYear,SoftwareDetectedStatus,SurveyorDetectedStatus,ManualCIV,ScientificName,CommonName,SpeciesCode,AutoRecognizerCode,Kingdom,Phylum,Class,Order,Family,Genus,Species,Surveyor1,Comment1,Surveyor2,Comment2,DurationMax_s,DurationMin_s,DurationMed_s,DurationMean_s,QualityMax,QualityMin,QualityMed,QualityMean,ScoreMax,ScoreMin,ScoreMed,ScoreMean,LevelMax_dB,LevelMin_dB,LevelMed_dB,LevelMean_dB,Hydroperiod,SMOrientation,DeploymentDate,FirstRecordDate,LastRecordDate,Firmware,Model,HighPassFilter_Hz,SamplingRate_Hz,Gain_dB,Preamp_dB,AvgTemperature_C,AvgPower_V,WavDuration_s,WavSize_B,RecordingLength_Hrs,Duration_FLAG,NoiseComment_FLAG`.

No inference is made from these header fields alone.

## Frozen retrieval correction

- **Download and hash only** the official frog table asset 763377 (~68.6 MB) and authoritative NPS metadata XML 763466 (~131 kB). Max cap 90 MB and 2 MB, respectively. The large 282 MB hourly temperature file is **not needed for initial taxon×recording grain QA**; its public size, name and source identity remain recorded, no data read from it. `AvgTemperature_C` in the frog table is a prospective candidate environmental covariate after quality checks.
- Never commit or upload raw NPS files, recording IDs or fine GPS data. Retain only aggregate source-only QA JSON; pin source byte SHA256 in the receipt **before detection outcomes are read**.
- Parse only key/metadata columns (`FileName,ParkCode,SiteLocation,StartTime,EventYear,ScientificName,SpeciesCode,Hydroperiod,AvgTemperature_C`) using pandas `usecols`. Do **not** load or summarize `SoftwareDetectedStatus`, `SurveyorDetectedStatus`, `ManualCIV` or any acoustic energy/quality outcomes.
- Count unique recording/event keys `ParkCode × SiteLocation × FileName × StartTime`, site count, taxa labels and number of taxon rows **per recording**. Distinguish repeated species rows from complete negative detections.
- Report exact missingness of required keys, event-year coverage (2016–2023), per-event taxon row multiplicity, whether full 14-taxon panel exists and whether both named *Lithobates catesbeianus* and *L. clamitans* units occur (including documented *Rana* synonyms).
- If the 14-row per-file assumption fails, fail closed on modeling nondetection **until original XML field descriptions establish exact row semantics**. Do not transform omitted species to zeros.
- Eligible if ≥80 distinct recording events containing a **complete explicit species monitoring panel**, ≥20 physical sites, ≥2 park units, and both named taxon units present. Survey counts are provenance, not scientific signal until fields `SurveyorDetectedStatus` and `ManualCIV` have a validated response codebook.
- Any lack of a complete panel, nonunique site/time key, unverified field codes, access failure or material missingness must be recorded and separately resolved before an independent heldout biological analysis.

## Biological boundary

If source passes, independently test bullfrog→green frog *predictive conditional association*, not NAAMP exact 10-stop checkerboard. A co-detection within a named recording is closer in time than NAAMP sequential stops, but does **not prove simultaneous calls**, frog-to-frog attraction, avoidance, shared vegetation or a trophic interaction. Hydroperiod is a source variable, **not directly measured macrophyte architecture**. First outcome model requires an independently frozen contract, no NAAMP parameter import.

No changes to frozen JAE RC6.
