"""Smoke-test the data-free release in Linux without workstation data."""
import argparse
from http.cookies import SimpleCookie
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.error
import urllib.request

APP = Path(__file__).resolve().parents[1] / ".render-preview"
PORT = int(os.environ.get("PORT", "18721"))
PROTECTED = ("capstone_final_outputs", "foundation_summaries", "final_research_exports",
             "local_research_sources", "research_overview_sources.json")


def health_check(server):
    started = time.perf_counter()
    url = f"http://127.0.0.1:{PORT}"
    deadline = started + 60
    while time.perf_counter() < deadline:
        if server.poll() is not None:
            raise RuntimeError(f"Streamlit exited during startup ({server.returncode}).")
        try:
            with urllib.request.urlopen(url + "/_stcore/health", timeout=1) as response:
                if response.status == 200:
                    break
        except OSError:
            time.sleep(0.1)
    else:
        raise RuntimeError("The configured port did not become healthy.")
    elapsed = time.perf_counter() - started

    expected = f"00000000:{PORT:04X}"
    with open("/proc/net/tcp", encoding="ascii") as table:
        if not any(row.split()[1:4:2] == [expected, "0A"] for row in table):
            raise RuntimeError("Streamlit is not listening on the requested wildcard IPv4 socket.")
    try:
        with urllib.request.urlopen(url + "/media/nonexistent.csv", timeout=2):
            raise RuntimeError("Unexpected media response.")
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            raise
    return elapsed


def live_session_check():
    from streamlit.proto.BackMsg_pb2 import BackMsg
    from streamlit.proto.ForwardMsg_pb2 import ForwardMsg
    from release_policy import PUBLIC_HOLD
    from websockets.sync.client import connect

    base = f"127.0.0.1:{PORT}"
    cookie = SimpleCookie()
    with urllib.request.urlopen(f"http://{base}/_stcore/health", timeout=3) as response:
        for value in response.headers.get_all("Set-Cookie", []):
            cookie.load(value)
    token = cookie["_streamlit_xsrf"].value
    headers = {"Cookie": "; ".join(f"{name}={item.coded_value}" for name, item in cookie.items())}
    types = set()
    found_hold = False
    request = BackMsg()
    request.rerun_script.SetInParent()
    with connect(f"ws://{base}/_stcore/stream", origin=f"http://{base}",
                 subprotocols=["streamlit", token], additional_headers=headers, open_timeout=10) as channel:
        channel.send(request.SerializeToString())
        for _ in range(250):
            frame = ForwardMsg.FromString(channel.recv(timeout=20))
            kind = frame.WhichOneof("type")
            if kind == "script_finished":
                break
            if kind != "delta" or not frame.delta.HasField("new_element"):
                continue
            element = frame.delta.new_element
            types.add(element.WhichOneof("type"))
            found_hold |= element.HasField("alert") and element.alert.body == PUBLIC_HOLD
        else:
            raise RuntimeError("The live Streamlit session did not finish.")
    assert found_hold
    assert not (types & {"arrow_data_frame", "arrow_table", "table", "download_button", "metric", "plotly_chart", "exception"})


def navigation_check():
    from streamlit.testing.v1 import AppTest
    from navigation import LABELS, RESEARCH_ROUTES, WAREHOUSE_ROUTES
    from release_policy import PUBLIC_HOLD

    app = AppTest.from_file(str(APP / "app.py")).run(timeout=30)
    assert app.title[0].value == "Research Overview"
    names = []
    elapsed_ms = []

    def visit(route):
        started = time.perf_counter()
        app.sidebar.button(key="nav_" + route).click().run(timeout=30)
        elapsed_ms.append((time.perf_counter() - started) * 1000)
        names.append(LABELS[route])
        assert not app.exception, (route, app.exception)
        assert len(app.title) == 1 and app.title[0].value == LABELS[route], route
        assert len(app.info) == 1 and app.info[0].value == PUBLIC_HOLD, route
        for element in ("metric", "plotly_chart", "dataframe", "table", "download_button", "selectbox"):
            assert not app.get(element), (route, element)

    for route in RESEARCH_ROUTES:
        visit(route)
    app.sidebar.button(key="nav_warehouse_track").click().run(timeout=30)
    for route in WAREHOUSE_ROUTES:
        visit(route)
    app.sidebar.button(key="nav_research_track").click().run(timeout=30)
    assert app.title[0].value == LABELS[RESEARCH_ROUTES[-1]]
    app.sidebar.button(key="nav_warehouse_track").click().run(timeout=30)
    assert app.title[0].value == LABELS[WAREHOUSE_ROUTES[-1]]
    return names, round(sum(elapsed_ms) / len(elapsed_ms), 1), round(max(elapsed_ms), 1)


def main():
    global APP
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", type=Path, default=APP, help="Freshly staged guarded runtime")
    APP = parser.parse_args().runtime.resolve(strict=True)
    sys.path.insert(0, str(APP))
    os.environ["PORT"] = str(PORT)
    if sys.platform != "linux" or sys.version_info[:3] != (3, 12, 10):
        raise RuntimeError("Use Linux with the planned Python 3.12.10 runtime.")
    for name in PROTECTED:
        if (APP / name).exists():
            raise RuntimeError(f"Private file or folder present: {name}")
    from deployment.page_publication import cfs_area_plan
    for filename in cfs_area_plan().files:
        if (APP / filename).exists():
            raise RuntimeError("A private CFS file is present in the runtime.")

    env = os.environ.copy()
    for name in ("CAPSTONE_DATA_DIR", "FINAL_RESEARCH_DATA_DIR", "PYTHONPATH", "PYTHONHOME"):
        env.pop(name, None)
        os.environ.pop(name, None)
    env["PORT"] = str(PORT)
    os.environ["WIQ_RELEASE_MODE"] = "public"
    # The normal production launcher sets the service release mode and uses the assigned port.
    server = subprocess.Popen([sys.executable, "run_dashboard.py", "render"], cwd=APP, env=env)
    try:
        startup = health_check(server)
        live_session_check()
        names, average, longest = navigation_check()
        for filename in cfs_area_plan().files:
            for prefix in ("", "media/", "app/static/"):
                url = f"http://127.0.0.1:{PORT}/{prefix}{filename}"
                try:
                    with urllib.request.urlopen(url, timeout=3) as response:
                        if response.headers.get_content_type() != "text/html":
                            raise RuntimeError("Unexpected runtime-file response.")
                except urllib.error.HTTPError as exc:
                    if exc.code != 404:
                        raise

        status = Path(f"/proc/{server.pid}/status").read_text(encoding="utf-8")
        peak_rss = int(next(line.split()[1] for line in status.splitlines() if line.startswith("VmHWM:")))
        print(json.dumps({
            "platform": sys.platform,
            "python": ".".join(map(str, sys.version_info[:3])),
            "listen_ipv4": "0.0.0.0",
            "assigned_port": PORT,
            "health_http": 200,
            "unknown_media_http": 404,
            "live_websocket_session": "guarded",
            "restricted_download_buttons": 0,
            "guarded_routes": names,
            "first_health_seconds": round(startup, 3),
            "mean_guarded_apptest_rerun_ms": average,
            "max_guarded_apptest_rerun_ms": longest,
            "streamlit_server_peak_rss_mib": round(peak_rss / 1024, 1),
        }, indent=2), flush=True)
    finally:
        server.terminate()
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=5)


if __name__ == "__main__":
    main()
