# Warehouse IQ navigation

The shared sidebar replaces the radio list and the separate Planning Insights
popover. All seven views now use one navigation surface and matching page titles.
The data remains archived academic research, not a live monitoring service.

## Information architecture

| Group | Display label | Existing route / renderer | Native Material icon |
|---|---|---|---|
| Workspace | Overview | Executive Overview | dashboard |
| Analytics | Demand Trends | Historical Demand | show_chart |
| Analytics | Warehouse Explorer | Warehouse Analytics | warehouse |
| Analytics | Model Performance | Model Comparison | bar_chart |
| Forecast & Planning | Demand Outlook | Future Forecasting | trending_up |
| Forecast & Planning | Planning Insights | Operational Insights | assignment |
| Research | Forecast Reliability | Model Validation | verified_user |

Material symbols are Streamlit's built-in equivalents of the requested dashboard,
line, warehouse, columns, trend, clipboard and checked-shield icons. Their labels
remain accessible text; icons are decorative.

## Implementation choice

`navigation.py` owns the ordered destination specification, labels, styling and
shared callback. Native `st.button` controls run the existing session-state router.
This retains the application's callback architecture, including Overview shortcuts,
without introducing a second page-state mechanism or a third-party dependency.
There is no hidden radio, JavaScript click handler or CSS-based routing. This is a
session-based application menu; it does not introduce URL deep links or browser
Back/Forward page history.

The single `navigation` state retains existing route names as internal identifiers.
The new business labels are presentation metadata. Invalid stale state resets to
Overview, and invalid callback destinations are rejected. All rendering functions,
forecast calculations and underlying data loaders keep their existing behavior.

## Visual specification

- 252px desktop sidebar, using Streamlit's native collapsible mobile drawer.
- Warehouse IQ wordmark, custom inline warehouse SVG and Demand Intelligence subtitle.
- Ink `#182e4c`, muted text `#4d5d73`, canvas `#fbfcfe`, active blue `#2866c9`,
  active fill `#e8f0fa` and hover fill `#edf1f6`.
- 19px brand, 13px menu text, 10px group labels; 43px minimum button targets.
- 3px active left indicator, soft background and bold label identify selection.
- Native Tab/Shift+Tab, Enter/Space activation; visible 3px focus outline.
- Reduced-motion preference disables transitions. No radio circles, refresh button,
  sidebar tables, excessive dividers or long research notes.
- Persistent Historical Study · 2014–2016 indicator and explicit archived status.
  Page content continues to display evaluation windows and December 2016 origins.

Menu styling uses authored `st.container(key=...)` classes. Width is a cosmetic
rule on the sidebar's accessible region name. No generated Emotion classes,
positional widget indexes, or selectors that control navigation are used. If the
cosmetic styles stop matching a future Streamlit DOM, native buttons and callbacks
continue to work. Sidebar collapse/expand remains owned by Streamlit.

## Scope and integrity

Updated app shell, navigation primitives, presentation titles and Overview shortcut
labels only. Removed Planning Insights' sidebar-hiding override and duplicate
popover. The six specialist analytical renderers and all calculation modules are
unchanged. Tests formerly driving the radio now drive the real sidebar buttons;
numerical regression expectations and download/filter checks remain intact.

The earlier Operational redesign's renderer-hash assertion covered a previous
UI-only scope. It now checks the separately captured calculation-module baseline,
because this task explicitly authorizes shared theme and Overview title edits.
The original 87-file source baseline has not been replaced or updated.

Validation results and desktop/mobile screenshots are recorded in
`NAVIGATION_QA.md`.
