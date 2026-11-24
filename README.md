# Warehouse IQ

Warehouse IQ retains the study navigation in a publication-gated release. The Data Foundation page can display CFS Area Record Coverage after the exact deployment and publication decisions have been verified. The original analytical renderers are included. Routes without verified data and independent release decisions show an availability notice. Original datasets and approvals are maintained privately.

## Deployable source

The Render build in [render.yaml](render.yaml) installs the pinned Python dependencies and stages the exact source allowlist. The launcher uses Render's assigned port and starts with static serving disabled. Auto-deploy is disabled in the reviewed configuration.

The [CFS package specification](docs/cfs_area_coverage_package.json) records the two runtime file pins. An authorized deployment receives those files only through the named production service's secret file at `/etc/secrets/warehouse-iq-cfs-area.json`. The approval and runtime files stay in private storage. Browser CSV downloads and public Git redistribution are excluded from the CFS release.

Run source integrity and guarded-route tests from a fresh checkout with Python 3.12.10 and the documented dependencies installed.

```bash
python -B verify_public_stage.py
python -B -m unittest discover -s tests
```

The chart describes counts of published estimate records by survey year and transportation-mode code. [BTS CFS Area File 2012–2022](https://data.bts.gov/d/j246-y2rf)

See the [navigation map](docs/NAVIGATION.md), [dashboard design](docs/DESIGN_SYSTEM.md) and [CFS release checkpoint](docs/CFS_AREA_COVERAGE_RELEASE.md).

On Linux, after staging the runtime, use `python -B deployment/linux_smoke.py --runtime .render-preview` to check the guarded startup and all routes.
