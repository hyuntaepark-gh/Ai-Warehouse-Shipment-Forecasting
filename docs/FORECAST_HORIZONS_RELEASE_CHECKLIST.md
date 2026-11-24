# Forecast Horizons release checklist

**Public release pending.** The separate configuration prepares a display-only pilot. The package specification contains hashes and metadata. It lists zero publication grants. [Exact pilot scope](public_data_package.json)

- [ ] Confirm applicable M5 and Favorita source terms and record the approving person, authority, date and evidence. Approve hosting for both summary CSVs and the sanitized source registry at their exact hashes and for the intended Render service ID.
- [ ] Approve full-precision chart and table display and the documented source attribution. [Page credits](../deployment/public_horizons_app.py)
- [ ] Record CSV download eligibility separately for M5 and Favorita. The display-only configuration keeps both downloads disabled.
- [ ] Approve the GitHub target and how to handle inherited archive files. Record any permission to distribute data through Git separately. Keep host data and decision evidence in private storage.
- [ ] Approve activation after reviewing the authorized payload and browser behavior.

## Build and run the guarded release

Create a code-only staging directory with:

~~~sh
python deployment/prepare_horizons_release.py stage <new-directory>
~~~

The [pilot Blueprint](../deployment/render.horizons.yaml) becomes the staged directory's root render.yaml. It runs Python 3.12.10 with pinned Linux dependencies, uses Render's PORT on 0.0.0.0 and checks /_stcore/health. Automatic deploys are disabled. The health endpoint also reports a healthy service while publication is held. [Render Blueprint reference](https://render.com/docs/blueprint-spec) · [Render port binding](https://render.com/docs/web-services#port-binding)

The gate requires a recorded hosting and display grant, exact byte hashes and a matching non-preview Render service. Approved data is supplied only through the service's private Secret File. Saving a Secret File can itself initiate deployment. [Preparation and gate](../deployment/public_horizons_gate.py) · [Render Secret Files](https://render.com/docs/configure-environment-variables#secret-files)
