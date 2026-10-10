"""Configuration from environment variables, validated at startup."""
import ipaddress
import logging
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

from .core.errors import ConfigError

PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = PACKAGE_DIR.parent
# Resolved from this file, never from the process cwd.
DEFAULT_SKILLS_ROOT = PROJECT_DIR.parent / "skillmasterclass"
DEFAULT_SYNONYMS_FILE = PROJECT_DIR / "config" / "synonyms.yaml"

TRANSPORTS = ("stdio", "http")
SEARCH_MODES = ("keyword", "semantic")
LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")


@dataclass(frozen=True)
class Config:
    skills_root: Path
    transport: str = "stdio"
    host: str = "127.0.0.1"
    port: int = 8765
    http_path: str = "/mcp"
    auth_token: str | None = field(default=None, repr=False)
    allowed_origins: tuple[str, ...] = ()
    log_level: str = "INFO"
    search_mode: str = "keyword"
    refresh_enabled: bool = True
    max_file_bytes: int = 1_000_000
    max_request_bytes: int = 1_000_000
    synonyms_file: Path | None = DEFAULT_SYNONYMS_FILE
    shared_dir: Path | None = None


def _bool(value: str, name: str) -> bool:
    v = value.strip().lower()
    if v in ("1", "true", "yes", "on"):
        return True
    if v in ("0", "false", "no", "off"):
        return False
    raise ConfigError(f"{name} must be true or false, got '{value}'.")


def _int(value: str, name: str, lo: int, hi: int) -> int:
    try:
        n = int(value)
    except ValueError:
        raise ConfigError(f"{name} must be an integer, got '{value}'.") from None
    if not lo <= n <= hi:
        raise ConfigError(f"{name} must be between {lo} and {hi}, got {n}.")
    return n


def _resolve_dir(value: str, name: str) -> Path:
    p = Path(value).expanduser()
    if not p.is_absolute():
        p = PROJECT_DIR / p  # relative paths are relative to the project, not cwd
    p = p.resolve()
    if not p.exists():
        raise ConfigError(f"{name} does not exist: {p}")
    if not p.is_dir():
        raise ConfigError(f"{name} is not a directory: {p}")
    return p


def is_loopback(host: str) -> bool:
    if host in ("localhost",):
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def load_config(env: dict | None = None) -> Config:
    env = os.environ if env is None else env
    g = lambda k, d=None: (env.get(k) or d)  # noqa: E731  empty string -> default

    root_raw = g("SKILLMASTERCLASS_ROOT")
    root = _resolve_dir(root_raw, "SKILLMASTERCLASS_ROOT") if root_raw else DEFAULT_SKILLS_ROOT.resolve()
    if not root_raw and not root.is_dir():
        raise ConfigError(f"Default skills directory not found: {root}. Set SKILLMASTERCLASS_ROOT.")

    transport = g("SKILLFINDER_TRANSPORT", "stdio").lower()
    if transport not in TRANSPORTS:
        raise ConfigError(f"SKILLFINDER_TRANSPORT must be one of {TRANSPORTS}, got '{transport}'.")

    search_mode = g("SKILLFINDER_SEARCH_MODE", "keyword").lower()
    if search_mode not in SEARCH_MODES:
        raise ConfigError(f"SKILLFINDER_SEARCH_MODE must be one of {SEARCH_MODES}, got '{search_mode}'.")

    log_level = g("SKILLFINDER_LOG_LEVEL", "INFO").upper()
    if log_level not in LOG_LEVELS:
        raise ConfigError(f"SKILLFINDER_LOG_LEVEL must be one of {LOG_LEVELS}, got '{log_level}'.")

    http_path = g("SKILLFINDER_HTTP_PATH", "/mcp")
    if not http_path.startswith("/"):
        raise ConfigError("SKILLFINDER_HTTP_PATH must start with '/'.")

    host = g("SKILLFINDER_HOST", "127.0.0.1")
    token = g("SKILLFINDER_AUTH_TOKEN")
    if token is not None and len(token) < 16:
        raise ConfigError("SKILLFINDER_AUTH_TOKEN must be at least 16 characters.")
    allow_remote = _bool(g("SKILLFINDER_ALLOW_REMOTE", "false"), "SKILLFINDER_ALLOW_REMOTE")
    if transport == "http":
        if not token:
            raise ConfigError("HTTP transport requires SKILLFINDER_AUTH_TOKEN (bearer token).")
        if not is_loopback(host) and not allow_remote:
            raise ConfigError(
                f"Refusing to bind HTTP to non-loopback host '{host}'. This server is localhost-only "
                "by default; set SKILLFINDER_ALLOW_REMOTE=true only behind TLS and a trusted network."
            )

    syn = g("SKILLFINDER_SYNONYMS_FILE")
    synonyms_file = Path(syn) if syn else DEFAULT_SYNONYMS_FILE
    if syn and not synonyms_file.is_absolute():
        synonyms_file = PROJECT_DIR / synonyms_file
    if syn and not synonyms_file.is_file():
        raise ConfigError(f"SKILLFINDER_SYNONYMS_FILE not found: {synonyms_file}")

    shared = g("SKILLFINDER_SHARED_DIR")

    origins = tuple(o.strip() for o in g("SKILLFINDER_ALLOWED_ORIGINS", "").split(",") if o.strip())

    return Config(
        skills_root=root,
        transport=transport,
        host=host,
        port=_int(g("SKILLFINDER_PORT", "8765"), "SKILLFINDER_PORT", 1, 65535),
        http_path=http_path,
        auth_token=token,
        allowed_origins=origins,
        log_level=log_level,
        search_mode=search_mode,
        refresh_enabled=_bool(g("SKILLFINDER_REFRESH_ENABLED", "true"), "SKILLFINDER_REFRESH_ENABLED"),
        max_file_bytes=_int(g("SKILLFINDER_MAX_FILE_BYTES", "1000000"), "SKILLFINDER_MAX_FILE_BYTES", 1024, 50_000_000),
        max_request_bytes=_int(g("SKILLFINDER_MAX_REQUEST_BYTES", "1000000"), "SKILLFINDER_MAX_REQUEST_BYTES", 1024, 50_000_000),
        synonyms_file=synonyms_file if synonyms_file.is_file() else None,
        shared_dir=_resolve_dir(shared, "SKILLFINDER_SHARED_DIR") if shared else None,
    )


def setup_logging(level: str) -> None:
    """Logs go to stderr only; stdout is reserved for the stdio protocol."""
    logging.basicConfig(
        level=level,
        stream=sys.stderr,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
