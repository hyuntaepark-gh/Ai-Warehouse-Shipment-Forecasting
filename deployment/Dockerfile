FROM python:3.12.10-slim-bookworm@sha256:97983fa8cc88343512862c62307159a82261c3528dc025f79e5a3f7af43e50b4
WORKDIR /opt/warehouse-iq
COPY app/requirements.txt linux-constraints.txt /tmp/warehouse-iq-deps/
RUN python -m pip install --no-cache-dir -r /tmp/warehouse-iq-deps/requirements.txt -c /tmp/warehouse-iq-deps/linux-constraints.txt \
    && python -m pip check \
    && useradd --create-home --uid 10001 warehouseiq
COPY app/ /opt/warehouse-iq/
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 WIQ_RELEASE_MODE=public
USER warehouseiq
CMD ["python", "run_dashboard.py", "render"]
