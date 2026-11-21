# Warehouse IQ — Cleaner Filter UI Patch

This patch is designed for your **latest local Codex project**, not the older ZIP copy. It **does not overwrite `app.py`, `navigation.py`, data CSVs, or forecasting calculations**.

## What changes

- Seven analytic page modules: radio-circle control groups become concise dropdown menus.
- Model Validation: evaluation period and metric appear alongside one another; year/model and temporal filters move into a collapsed *Refine results* section.
- Model Comparison, Warehouse Analytics, Future Forecasting, and Operational Insights: secondary model/warehouse filters move into short expandable filter sections.
- Existing selection values, options, keys and default horizons are preserved.
- Existing AppTest selectors referring to page radio controls are migrated to selectbox references where straightforward.
- Data source files are hashed before and after the patch.
- The current Codex navigation files are untouched.

## Apply to the CURRENT project

1. Close the Streamlit server and make a backup of your latest local project folder.
2. Copy `apply_simplified_controls.py` into the **project root** beside `app.py` (for example, `I:\Potforlio\Warehouse Demand Platform`).
3. In the VS Code terminal opened at that root, run:

```powershell
python apply_simplified_controls.py
python -m unittest discover -s tests -v
python -m streamlit run app.py
```

4. Check the Model Validation, Warehouse Analytics, and Planning Insights pages in the browser. Expand *Refine results* or *Choose warehouses* for advanced filters. Verify all 7 pages and their downloads.

## Rollback

The installer creates `.ui_backup/YYYYMMDD-HHMMSS` containing the original copies of every changed file. Restore those originals to the corresponding project paths if needed. The script is designed to be idempotent.

## Limits

The patch was syntax-checked and exercised against the **previously shared project archive**, using a mock Streamlit control and hash checks. It has **not** been executed in your latest local Codex workspace, and browser rendering/full AppTest tests of that latest copy remain necessary. If newer Codex edits have changed a filter block, the installer skips that optional layout change and reports it; it will not guess a replacement. Since the latest sidebar was modified after the last shared ZIP, this patch intentionally does not replace it.
