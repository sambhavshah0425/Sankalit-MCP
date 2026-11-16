import os
from pathlib import Path

# Project root directory (where sankalit-mcp source lives)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _parse_drive_map(raw: str) -> dict:
    r"""
    Parse SANKALIT_DRIVE_MAP into a {DRIVE_LETTER: UNC_Path} dict.

    Format (semicolon-separated entries, each 'LETTER=UNC'):
        Z=\\192.168.1.5\Sales;R=\\192.168.1.5\Marketing

    This lets callers pass mapped-drive paths like 'Z:\\10. Proposal\\...'
    and have them translated to the underlying UNC share, which is far more
    reliable than depending on the per-session drive mapping being visible
    to this (background) process.
    """
    mapping = {}
    if not raw:
        return mapping
    for entry in raw.split(";"):
        entry = entry.strip()
        if not entry or "=" not in entry:
            continue
        letter, unc = entry.split("=", 1)
        letter = letter.strip().rstrip(":").upper()
        unc = unc.strip()
        if letter and unc:
            mapping[letter] = Path(unc)
    return mapping


DRIVE_MAP = _parse_drive_map(os.getenv("SANKALIT_DRIVE_MAP", ""))


def canonicalize(raw) -> Path:
    r"""
    Bring a path to a canonical, comparable form WITHOUT following inner
    symlinks/junctions:
      1. Translate a mapped drive letter (e.g. 'Z:') to its UNC share via
         DRIVE_MAP when configured.
      2. Resolve only the drive/anchor (e.g. 'Z:\\' or '\\\\host\\share\\')
         so mapped drives and UNC paths compare equal.
    Inner path components are left untouched so sandboxing stays strict.
    """
    raw = Path(raw)

    # 1. Drive-letter translation (only for real drive letters like 'Z:',
    #    never for UNC anchors such as '\\host\share' which contain no colon).
    if raw.drive and ":" in raw.drive:
        letter = raw.drive.rstrip(":").upper()
        if letter in DRIVE_MAP:
            try:
                rel = raw.relative_to(raw.anchor) if raw.anchor else raw
            except ValueError:
                rel = Path()
            mapped = DRIVE_MAP[letter]
            raw = mapped if str(rel) in (".", "") else mapped / rel

    # 2. Resolve just the anchor (drive root / UNC share root).
    if raw.anchor:
        try:
            resolved_anchor = Path(raw.anchor).resolve()
            rel = raw.relative_to(raw.anchor)
            raw = resolved_anchor if str(rel) in (".", "") else resolved_anchor / rel
        except Exception:
            pass

    return raw


def _fallback_root() -> Path:
    """Choose a safe default root when SANKALIT_WORKSPACE is not set."""
    cwd = Path.cwd()
    cwd_resolved = cwd.resolve()
    # Guard against GUI launch defaults (Windows launches from System32) and
    # against accidentally exposing an entire drive root.
    if "system32" in str(cwd_resolved).lower() or cwd_resolved == cwd_resolved.anchor:
        return PROJECT_ROOT
    return cwd_resolved


def _parse_workspace_roots() -> list:
    r"""
    Parse SANKALIT_WORKSPACE into a list of allowed workspace roots.

    Accepts one OR many roots, semicolon-separated, e.g.:
        \\192.168.1.5\Sales;\\192.168.1.5\Marketing;Z:\
    A path is allowed if it lives inside ANY of these roots.
    """
    env_workspace = os.getenv("SANKALIT_WORKSPACE", "")
    roots = []
    if env_workspace:
        for part in env_workspace.split(";"):
            part = part.strip()
            if not part:
                continue
            roots.append(canonicalize(part))
    if roots:
        return roots
    return [_fallback_root()]


# All roots the server is allowed to touch. Sandbox check passes if a path is
# inside any one of these.
WORKSPACE_ROOTS = _parse_workspace_roots()

# Primary root: used as the base for resolving relative paths, and kept for
# backward compatibility with code/tests that reference a single root.
WORKSPACE_ROOT = WORKSPACE_ROOTS[0]
ROOT_DIRECTORY = WORKSPACE_ROOT

# Supported file extensions
SUPPORTED_EXTENSIONS = {
    ".txt",
    ".md",
    ".docx",
    ".pdf",
    ".xlsx",
    ".pptx",
}

# Default behaviour
DEFAULT_OVERWRITE = False
CREATE_PARENT_DIRECTORIES = True
