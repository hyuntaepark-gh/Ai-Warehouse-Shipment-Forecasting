# CFS Area Record Coverage release checkpoint

The owner conditionally approved Render hosting and full-precision browser display for this Data Foundation chart. Public GitHub data distribution and CSV downloads are denied. The production service identity, deployed revision, and final release authorization must be verified before activation.

The [package specification](cfs_area_coverage_package.json) supplies the exact two file names and SHA-256 values. The runtime excludes raw survey records and all other research data. The chart attributes the U.S. Census Bureau and Bureau of Transportation Statistics and displays counts of published estimate records by survey year and transportation mode. [BTS CFS Area File 2012–2022](https://data.bts.gov/d/j246-y2rf)

## Production verification

1. In Render, select the service whose hostname matches the intended production website. Record the actual service ID and live deployment SHA. Verify the linked repository, branch, build command, start command, Python version, and names of any runtime secret files. Keep secret contents private.
2. Compare the settings with [the reviewed configuration](../render.yaml). Use the assigned port, disabled static serving and the guarded launcher. Confirm the exact commit and record the repository disposition before approving publication.
3. Keep the conditional record inactive until the owner confirms the exact service, reviewed deployment, data pins and display scope. Verify completed decisions using `python -m deployment.page_publication "Data Foundation" --section cfs-area-coverage --authorization <decision.json> --service-id <service-id>`.
4. After final authorization, provision the exact two-file envelope through a service-level Render secret named `warehouse-iq-cfs-area.json`. The public gate reads only `/etc/secrets/warehouse-iq-cfs-area.json` on the verified non-preview service. Keep the data, decision records and envelope off Git. Verify chart attribution, all route holds and direct access denial after any authorized manual deployment. [Render secret-file settings](https://render.com/docs/configure-environment-variables)
