"""H. Real transports: stdio subprocess and Streamable HTTP server."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import urllib.error
import urllib.request
import pytest
from fastmcp import Client
from fastmcp.client.transports import StdioTransport, StreamableHttpTransport

from tests.conftest import free_port

PROJECT = Path(__file__).resolve().parents[1]
TOKEN = "test-token-0123456789abcdef"


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith(("SKILLFINDER_", "SKILLMASTERCLASS_"))}
    e["PYTHONPATH"] = str(PROJECT)
    e.update(extra)
    return e


async def test_stdio_end_to_end(tmp_path):
    # cwd deliberately NOT the project, to prove paths don't depend on it
    t = StdioTransport(command=sys.executable, args=["-m", "skillfinder_mcp"], env=env(), cwd=str(tmp_path))
    async with Client(t) as c:
        assert len(await c.list_tools()) == 12
        r = await c.call_tool("search_skills", {"query": "Playwright API testing", "limit": 1})
        assert r.data["results"][0]["id"] == "pw-api-tester"


def test_stdio_stdout_is_protocol_only(tmp_path):
    init = {"jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                       "clientInfo": {"name": "t", "version": "1"}}}
    p = subprocess.run([sys.executable, "-m", "skillfinder_mcp"], input=json.dumps(init) + "\n",
                       capture_output=True, text=True, env=env(SKILLFINDER_LOG_LEVEL="DEBUG"),
                       cwd=str(tmp_path), timeout=60)
    lines = [l for l in p.stdout.splitlines() if l.strip()]
    assert lines, p.stderr
    for l in lines:
        assert json.loads(l)["jsonrpc"] == "2.0"  # every stdout line is JSON-RPC
    assert "Indexed" in p.stderr  # diagnostics go to stderr


def test_bad_config_exits_cleanly(tmp_path):
    p = subprocess.run([sys.executable, "-m", "skillfinder_mcp"], capture_output=True, text=True,
                       env=env(SKILLMASTERCLASS_ROOT=str(tmp_path / "missing")), timeout=60)
    assert p.returncode == 2 and "Configuration error" in p.stderr and p.stdout == ""


@pytest.fixture(scope="module")
def http_server():
    port = free_port()
    proc = subprocess.Popen([sys.executable, "-m", "skillfinder_mcp"],
                            env=env(SKILLFINDER_TRANSPORT="http", SKILLFINDER_PORT=str(port),
                                    SKILLFINDER_AUTH_TOKEN=TOKEN, SKILLFINDER_MAX_REQUEST_BYTES="20000"),
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=str(PROJECT))
    url = f"http://127.0.0.1:{port}/mcp"
    for _ in range(100):
        try:
            urllib.request.urlopen(url, timeout=0.5)
            break
        except urllib.error.HTTPError:
            break  # server is up (it answered, even if with an error status)
        except OSError:
            time.sleep(0.2)
    else:
        proc.kill()
        pytest.fail("HTTP server did not start: " + proc.stderr.read().decode(errors="replace"))
    yield url
    proc.terminate()
    try:
        proc.wait(10)
    except subprocess.TimeoutExpired:
        proc.kill()


async def test_http_end_to_end_with_token(http_server):
    t = StreamableHttpTransport(http_server, headers={"Authorization": f"Bearer {TOKEN}"})
    async with Client(t) as c:
        assert len(await c.list_tools()) == 12
        r = await c.call_tool("search_skills", {"query": "test strategy", "limit": 1})
        assert r.data["results"][0]["id"] == "test-strategy-creator"
        assert len(await c.list_prompts()) == 12


INIT = {"jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "t", "version": "1"}}}
HDRS = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json"}


def post(url, body: bytes | dict, headers: dict) -> int:
    data = body if isinstance(body, bytes) else json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code


def test_http_rejects_missing_or_wrong_token(http_server):
    assert post(http_server, INIT, HDRS) == 401
    bad = {**HDRS, "Authorization": "Bearer wrong-token-000000000"}
    assert post(http_server, INIT, bad) == 401


def test_http_rejects_foreign_origin(http_server):
    h = {**HDRS, "Authorization": f"Bearer {TOKEN}", "Origin": "https://evil.example"}
    assert post(http_server, INIT, h) == 403


def test_http_rejects_foreign_host_header(http_server):
    h = {**HDRS, "Authorization": f"Bearer {TOKEN}", "Host": "attacker.example"}
    assert post(http_server, INIT, h) == 421


def test_http_rejects_oversized_body(http_server):
    h = {**HDRS, "Authorization": f"Bearer {TOKEN}"}
    big = dict(INIT, params=dict(INIT["params"], padding="x" * 50_000))
    assert post(http_server, big, h) == 413


def test_http_malformed_request(http_server):
    h = {**HDRS, "Authorization": f"Bearer {TOKEN}"}
    assert 400 <= post(http_server, b"{not json", h) < 500
