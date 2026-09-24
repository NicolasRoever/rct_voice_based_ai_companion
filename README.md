# Replication Package for: A randomised controlled trial of a voice-based generative AI emotional support companion

This repository contains the anonymzed raw data and code to reproduce the analyses presented in the paper.

If you have any questions, contact the corresponding author: 

> Nicolas Roever, M.Sc. //
> University of Cologne, Germany //
> Email: nicolas.roever@wiso.uni-koeln.de //
> WWW: [https://nicolasroever.com](https://nicolasroever.com) //

## Run

Install [pixi](https://pixi.sh), open a terminal in this folder, then:

```sh
pixi install --locked
pixi run replicate
pixi run test
```

## Folders

| Folder | Contents |
|---|---|
| `data/` | Trial data, screening responses and aggregate safety counts, benchmarks and dictionary |
| `src/replication/` | Analysis functions and small `task_*.py` files, grouped by topic |
| `validation/` | Original reported numbers and input provenance |
| `tests/` | Scoring, denominator, time-window and public-data checks |
| `bld/` | Rebuilt data, results, tables, figures and manuscript |

All paths are defined in `src/replication/config.py`. Functions take their
inputs as arguments and return results. Tasks read and save files.
`bld/` can be deleted and rebuilt with `pixi run replicate`.

## Find a result

| Manuscript item | Output under `bld/` |
|---|---|
| Table 1: symptom outcomes | `manuscript/tables_python/main_results_psych.tex` |
| Table 2: categorical outcomes | `manuscript/tables_python/clinical_outcomes_main.tex` |
| Table A1: baseline characteristics | `manuscript/tables_python/balance_table_rct.tex` |
| Table A2: robustness | `manuscript/tables_python/effect_robustness_wave_4.tex` |
| Figure 1: participant flow | `manuscript/figures_python/consort_diagram_w124.pdf` |
| Figures A4–A5: symptom changes | `manuscript/figures_python/*baseline_vs_w4*.pdf` |
| Figure A6: published benchmarks | `manuscript/figures_python/metaanalysis_digital_*.pdf` |
| Engagement, safety, power, text values | `results/*.json` and `results/*.csv` |
| Replication checks | `results/validation.json`, `results/manuscript_comparison.csv` |

Architecture, advertisement and application screenshots (Figures A1–A3),
study descriptions (Table A3), protocol, and research-team adjudications
are supplied documentary material. Published study estimates are fixed
inputs; this trial's benchmark estimates are calculated from its regressions.

## Data and analysis conventions

The original project creates these data in `task_anonymize_medicine_data`
(`src/sonia_project/waitlist_trial/overall_analysis/task_create_public_data.py`).
Its four CSV outputs are copied here unchanged. `validation/input_provenance.json`
records their hashes; the pipeline verifies them before accepting the results.


- `participants.csv` has the 400 randomized participants, with new IDs and
  shuffled rows. The first-400 selection was verified before export; original
  dates, source IDs and survey timing fields are not distributed.
- `screening.csv` retains all 10,490 screener respondents. Rows are shuffled,
  with no IDs or dates. It supplies the full GAD-7 reference distribution and
  the CONSORT screening counts.
- Safety events and manually coded concerns are aggregate, unlinked inputs.
  No participant dates, transcripts, free-text responses or linked crisis
  records are included. The retained survey and demographic data are real.
- Wave 1 is screening, wave 2 is baseline, and wave 4 is the two-week follow-up.
  The input contains selected valid responses, including three UCLA-3 items.
  Private survey deduplication and safety adjudication precede this package.
- ANCOVA uses HC3 standard errors. GAD-7 standardization uses the full screener
  responses; PHQ-8 uses the 400 randomized participants. Missing follow-up
  scores are not imputed. PHQ-8 improvement outcomes require baseline ≥10.
- Usage columns give days relative to each UTC randomization date. Weekly
  windows are days −1–6 and 7–13; nonusers count as zero. SDs use `ddof=1`.
- Power calculations are prospective planning calculations; the ANCOVA power
  uses the stated baseline-correlation approximation.

## Reuse

The code retains the source repository's MIT notice in `LICENSE`.
Study data and their dictionary are licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); see `LICENSE_DATA`.
Use `CITATION.cff` to cite this package. The manuscript and third-party material retain their existing rights.
