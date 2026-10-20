# Warehouse IQ navigation QA

Verified on October 16, 2026 with Streamlit 1.66.0 and the actual Capstone exports.

## Automated validation

- Complete suite: **105 tests passed**, including all 99 existing regressions and
  six new navigation tests. See `navigation_test_output.txt`.
- After the final heading-spacing adjustment, all six navigation tests passed
  again. See `navigation_interaction_test_output.txt`.
- Every destination renders its correct business title and one selected route.
- Seven native sidebar buttons; no sidebar radio or duplicate Planning popover.
- Overview shortcuts reach the existing routes and clear Overview-only content.
- Current-page reselection retains the Demand Trends year filter and downloads.
- Existing metric, cohort-separation, missing-data, filter and CSV-download
  regressions still pass against the actual source files.
- Invalid route callbacks are rejected; stale saved route state recovers safely.
- **87 / 87 original source hashes match** `source_hashes_before.json`.
- **8 / 8 calculation and loading module hashes match** the baseline captured
  before the navigation edits. No source or calculation baseline was regenerated
  to accept changes.

## Browser checks

All seven sidebar destinations were clicked in the running browser. Each displayed
its expected title and retained the shared sidebar:

| Destination | Result |
|---|---|
| Overview | Pass |
| Demand Trends | Pass |
| Warehouse Explorer | Pass |
| Model Performance | Pass |
| Demand Outlook | Pass |
| Planning Insights | Pass |
| Forecast Reliability | Pass |

- Desktop sidebar measured **252 CSS pixels**, within the requested 240–260px.
- Mobile tested at **390 × 844**: native drawer expansion/collapse and navigation
  to Forecast Reliability work. All seven destinations and the study indicator fit
  in the expanded drawer; long pages continue to scroll normally.
- Tab moves from Overview to Demand Trends. The focused button has a visible
  `#2866c9` 3px outline. Enter and Space activated the expected destination.
- Heading group spacing was corrected after visual inspection, using authored
  container keys rather than generated CSS class names.
- Streamlit restarted successfully; `/_stcore/health` returned **HTTP 200**.
- The native session router remains unchanged in scope: browser URL history and
  shareable page deep links are not newly introduced.

## Screenshots

Screenshots are original browser captures, not mockups or composited images.

- [Desktop, 1440 × 1000](navigation/sidebar_desktop_1440.jpg)
- [Mobile drawer, 390 × 844](navigation/sidebar_mobile_390.jpg)

The research dates, cohort caveats, archived December 2016 forecast origin and
full-precision downloads remain in the appropriate page content. The sidebar
retains only the small historical-study and archived-status indicators.
