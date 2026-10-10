"""Error types shared by the core services. No MCP imports."""


class ConfigError(Exception):
    """Invalid or missing configuration. Fatal at startup."""


class SkillError(Exception):
    """User-facing error with a stable code, e.g. not_found or ambiguous."""

    def __init__(self, code: str, message: str, **details):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details

    def to_dict(self) -> dict:
        return {"code": self.code, "message": self.message, **self.details}

    def __str__(self) -> str:
        extra = ""
        if self.details.get("candidates"):
            extra = f" Candidates: {', '.join(self.details['candidates'])}"
        return f"[{self.code}] {self.message}{extra}"
