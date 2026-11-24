# Navigation verification

Run the public-source tests from a clean checkout:

```bash
python -B -m unittest discover -s tests
```

The route tests drive the native sidebar buttons through both research tracks
and verify all 13 labels. They check the publication hold, the lack of download
controls and the Data Foundation renderer dispatch. The dispatch test uses a
mocked gate and provides no authorization or research data.

For the guarded Linux startup and route checks, use the procedure in the
[project README](../README.md).
