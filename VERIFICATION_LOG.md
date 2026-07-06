# Verification Log

## 2026-07-06 — Analysis-only zip of investment_geometry + geoapp compatibility

1. **Output**: `out/zipped/investment_geometry_analysis.zip` (1.07 GB uncompressed content, 39,936 entries)
   - **How verified**: `unzip -l` entry count; extracted the full archive to scratchpad and listed the tree: contains `analysis/` (pca, embeddings, linear_probe, trajectories, relpos_counts.json), `config.json`, `summary.json`, `data/metadata.json`, `data/prompt_dataset.json`, and 4,588 sample dirs each with exactly `choice.json`, `prompt_sample.json`, `preference_sample.json`, `position_mapping.json`. Zero `.npy` raw-activation files under `data/` (18,354 JSONs added = 4,588×4 + 2).
   - **Result**: VERIFIED

2. **Output**: Original `out/geo/investment_geometry/data/` untouched
   - **How verified**: zip/find operations were read-only; after all work, re-listed `data/samples` (4,588 dirs) and `data/samples/sample_0/L0/*.npy` still present.
   - **Result**: VERIFIED

3. **Output**: `src/intertemporal/geoapp/data_loader.py` — analysis-only-bundle support (layers fall back to `summary.json`; `get_valid_sample_indices` falls back to position-mapping validity when no activations shipped)
   - **How verified**:
     - Mapping-derived validity vs npy-based validity on FULL real data: 126/126 targets identical (all 38 positions × 3 layers × 2 components + per-rel_pos variants) — `scratchpad/check_mapping_validity.py`.
     - Patched loader on zip-extracted data vs real data: 126/126 targets identical indices, identical layer discovery — `scratchpad/check_zip_equivalence.py`.
     - Real-data code path unchanged (same npy `any()` check; summary load reordered before `_discover_targets`, used only in fallback).
   - **Result**: VERIFIED

4. **Output**: geoapp server works on zip-extracted data
   - **How verified**: ran two servers (zip data :8765, real data :8766); diffed 16 endpoints (config, 5 embeddings incl. previously-broken `time_horizon` and per-rel_pos, 2 metadata colorings, 2 samples, metrics, heatmap, trajectory, tokens, scree, alignment): 15/16 byte-identical; `/config` semantically identical (all 13 keys compare equal, byte diff is JSON ordering only).
   - **Result**: VERIFIED

5. **Output**: geoapp UI works on zip-extracted data
   - **How verified**: started backend :8000 (zip data) + Vite dev server :3000; rendered `http://localhost:3000/investment_geometry` in headless Chrome and viewed the screenshot with image tokens: 3D PCA point cloud renders, "4,588 / 4,588 visible", 12 layers · 17 positions header, token/position panel populated, Time Horizon legend active (`scratchpad/ui_dev_zip.png`).
   - Production static mount (`/` on backend) serves index.html but has no SPA fallback for `/dataset` sub-paths — identical behavior on real data (pre-existing, not zip-related).
   - **Result**: VERIFIED

6. **Output**: branch working-tree deletions undone (118 files, `src/common/` etc.)
   - **How verified**: `git ls-files --deleted` → 0; `git status --short` shows only the intentional `data_loader.py` modification and pre-existing untracked dirs; `src/common/auto_export.py` present; geoapp imports resolve (servers ran from main repo).
   - **Result**: VERIFIED

## 2026-07-06 — geo bundle published to GitHub release `geo-bundles`

7. **Output**: Release `geo-bundles` with `investment_geometry_analysis.zip` split into 20×25MB parts + `.manifest` (21 assets)
   - **How verified**: local network corrupted large TLS uploads ("bad record MAC"; sandbox made it worse but 488MB failed even unsandboxed), so the bundle ships as parts. All 21 assets listed via API and matched against local files by name+size; then the full set was downloaded back from the public release URLs, reassembled, and SHA-256 compared: downloaded == local == manifest hash (8de28908…162b). Manifest flow of `run_geoapp_bundle.sh` tested end-to-end locally (assemble, checksum OK, 4,588 samples extracted, idempotent re-run, no-overwrite guard).
   - **Result**: VERIFIED
