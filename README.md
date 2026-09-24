# Sonia trial: replication package

Reproduces the figures, tables and key numbers from the medicine revision.
The full manuscript is not included. Automated safety-event and escalation
counts are excluded at the author's request.

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
| `data/` | Trial and screening data, survey concern categories, benchmarks and supplied exhibits |
| `src/replication/` | Analysis functions, small pytask files and table templates |
| `validation/` | Reported numerical references and input provenance |
| `tests/` | Scoring, denominator, time-window and data checks |
| `bld/figures/` | Seven generated PDFs and supplied illustrations |
| `bld/tables/` | Four calculated LaTeX tables and the supplied study-comparison table |
| `bld/results/` | Key numbers, detailed estimates and validation results |
| `bld/clean_data/` | Scored analysis data |

Paths are defined in `src/replication/config.py`. Functions take inputs and
return results; tasks read and save files. Delete `bld/` and rerun to rebuild.

## Find a result

| Exhibit | Output under `bld/` |
|---|---|
| Table 1: symptom outcomes | `tables/main_results_psych.tex` |
| Table 2: categorical outcomes | `tables/clinical_outcomes_main.tex` |
| Table A1: baseline characteristics | `tables/balance_table_rct.tex` |
| Table A2: robustness | `tables/effect_robustness_wave_4.tex` |
| Table A3: study comparison | `tables/study_comparison.tex` |
| Figure 1: participant flow | `figures/consort_diagram_w124.pdf` |
| Figures A1–A3: supplied illustrations | `figures/*.png`, `figures/*.PNG` |
| Figures A4–A5: symptom changes | `figures/*baseline_vs_w4*.pdf` |
| Figure A6: published benchmarks | `figures/metaanalysis_digital_*.pdf` |
| Key numbers | `results/key_numbers.csv`, `results/key_numbers.json` |
| Replication checks | `results/validation.json`, `results/key_numbers_comparison.csv` |

Illustrations and the study-comparison table are supplied inputs. Published
benchmark estimates are fixed; this trial's estimates are recalculated.
Tables are LaTeX fragments for inclusion in a document.

## Data and methods

The original project's `task_anonymize_medicine_data` creates three CSV files:
`participants.csv`, `screening.csv` and `safety_concern_categories.csv`.
They are copied here unchanged. The pipeline verifies their hashes against
`validation/input_provenance.json`. See `data/data_dictionary.csv` for fields.

- The trial file contains 400 randomized participants with release-only IDs.
  The separate screening file retains all 10,490 respondents without IDs or dates.
  The first-400 selection is verified before export.
- Survey safety concerns are coded into unlinked categories. Transcripts,
  free-text responses, participant dates and crisis-event records are excluded.
- Wave 1 is screening, wave 2 is baseline, and wave 4 is the two-week follow-up.
  Survey selection and deduplication take place in the original project.
- ANCOVA uses HC3 standard errors. GAD-7 standardization uses all screeners;
  PHQ-8 uses the 400 randomized participants. Missing follow-ups are not imputed.
  PHQ-8 improvement outcomes require baseline ≥10.
- Usage windows are days −1–6 and 7–13 relative to each UTC randomization date;
  nonusers count as zero. SDs use `ddof=1`.
- Power calculations use the stated prospective assumptions; ANCOVA power
  uses a baseline-correlation approximation.

Validation checks 154 retained reported values, eight table sample-size entries,
robustness-table numbers and stars, and all coefficients of the four main models.
Reference values are used only for validation.

## Reuse

Code: MIT (`LICENSE`). Study data and dictionary: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (`LICENSE_DATA`).
Use `CITATION.cff` for attribution. Supplied third-party material retains its own rights.
