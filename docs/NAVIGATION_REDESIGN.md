# Navigation design

Warehouse IQ uses a single Streamlit sidebar with two research tracks. Read the
[current route map](NAVIGATION.md) for the complete list of 13 routes.

Native buttons and a shared session-state callback implement navigation. The
sidebar maintains the most recent route for each research track and rejects
invalid route names. The active-page label, visible keyboard focus, and native
mobile drawer remain available independently of the visual styling.

The guarded build keeps all route labels available. Data Foundation contains the
CFS renderer. Display of its exact data depends on the
[publication gate](CFS_AREA_COVERAGE_RELEASE.md).
