# Multi-criteria ambulance routing in Sidi Bel Abbès: data and code

Data, code and results for the paper *Exact multi-criteria ambulance routing on OpenStreetMap data: a benchmark of multi-objective search algorithms in Sidi Bel Abbès, Algeria* (submitted to the Turkish Journal of Electrical Engineering & Computer Sciences).

The repository lets you:

- rebuild the road network of Sidi Bel Abbès (Algeria) with its speed bumps, traffic signals, stop and give-way signs, crossings, barriers and one-way streets from OpenStreetMap;
- rerun the benchmark of exact multi-objective shortest-path algorithms (BOA\*, NAMOA\*dr, EMOA\*, LTMOA\*, Martins) on 200 patient-to-hospital queries;
- recompute every table and figure of the paper from the stored results.

## Contents

| Folder | What it holds |
|---|---|
| `notebook/` | `FEDZ_TrackB_v3_multicriteria_benchmark.ipynb`, the Google Colab notebook that downloads the data, builds the criteria, compiles the original algorithm codes and runs the benchmark. `fedz_offline_fixture_v3.py` is a synthetic city used only to test the notebook without internet. |
| `data/` | `arcs_criteria.csv`: one row per arc (15,792 arcs) with all criteria. `sba_drive_network_v3.graphml`: the drivable network used in the paper (5683 nodes), readable with OSMnx. |
| `results/` | `run_metadata.json` (configuration, OSM counts, code commits, hardware), `FEDZ_TrackB_v3_executed_colab.ipynb` (the run reported in the paper), `raw/` (one row per query and algorithm), `tables/` (CSV and LaTeX), `figures/` (notebook figures), `paper_figures/` (Figures 1 and 2 of the paper). |
| `scripts/` | `reproduce_statistics.py` (Pareto-set statistics of Table 2 and the heuristic/search split of Table 4), `make_tables.py`, `make_figures.py`. |

### Columns of `data/arcs_criteria.csv`

| Column | Meaning |
|---|---|
| `u`, `v` | OSM node ids of the arc tail and head |
| `length` | length in metres |
| `speed` | speed limit in km/h (OSM `maxspeed`, else 40 km/h) |
| `highway`, `oneway`, `surface` | OSM tags |
| `bumps`, `signals`, `stops`, `crossings` | number of speed bumps, traffic signals, stop/give-way signs and crossings counted on the arc |
| `interruptions` | `signals + stops` |
| `unpaved_m` | unpaved length in metres (0 everywhere in this extract) |
| `contra_m` | length driven against a one-way street (contraflow scenario only) |
| `time_s` | travel time in seconds, including the slow-down at bumps |
| `time` | travel time in units of 0.1 s (integer cost used by the algorithms) |

## Reproducing the results

**Full benchmark (about 30–90 min).** Open `notebook/FEDZ_TrackB_v3_multicriteria_benchmark.ipynb` in Google Colab, choose a CPU runtime and run all cells. The notebook clones and compiles the original codes of BOA\*/NAMOA\*dr ([jorgebaier/BOAstar](https://github.com/jorgebaier/BOAstar), commit 4dd21e6, MIT licence) and EMOA\* ([rap-lab-org/public_emoa](https://github.com/rap-lab-org/public_emoa), commit 6ca88f2). These codes are not redistributed here. OpenStreetMap changes over time, so a new download can differ slightly from `data/`.

**Statistics, tables and figures from the stored data (a few minutes).**

```bash
pip install -r requirements.txt
# EMOA* binary for the search-time split (build it as in the notebook)
EMOA_BIN=/path/to/public_emoa/build/run_emoa python scripts/reproduce_statistics.py
python scripts/make_tables.py
python scripts/make_figures.py
```

`reproduce_statistics.py` rebuilds the 200 queries from `data/arcs_criteria.csv` and checks that every Pareto set has the same size as in the Colab run. Its outputs go to `results/reproduced/`. The front statistics are deterministic. Timings depend on the machine.

Hardware of the reported runs: Google Colab CPU runtime (AMD EPYC 7B12) for the main benchmark, Intel Xeon 2.80 GHz for the heuristic/search split.

## Licences

- Code (`notebook/`, `scripts/`): MIT licence, see `LICENSE`.
- Data (`data/` and results derived from OpenStreetMap): © OpenStreetMap contributors, available under the Open Database License (ODbL) 1.0, see `DATA_LICENSE.md`.

## Citation

If you use this repository, please cite the paper and the repository (see `CITATION.cff`).
