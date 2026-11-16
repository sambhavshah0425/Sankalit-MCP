import os
from pathlib import Path


def _allowed_roots(config) -> list:
    """
    Build the list of allowed roots for the current call.

    Merges config.WORKSPACE_ROOTS with config.WORKSPACE_ROOT so that code (or
    tests) that patch only the single WORKSPACE_ROOT still work, and so newer
    multi-root configuration is honoured.
    """
    roots = []
    extra = getattr(config, "WORKSPACE_ROOTS", None)
    if extra:
        roots.extend(extra)
    primary = getattr(config, "WORKSPACE_ROOT", None)
    if primary is not None and primary not in roots:
        roots.append(primary)
    return roots


def resolve_path(relative_or_abs_path: str | Path) -> Path:
    r"""
    Resolve a path and ensure it stays strictly inside one of the allowed
    workspace roots (config.WORKSPACE_ROOTS).

    - Relative paths are resolved against the primary root (config.WORKSPACE_ROOT).
    - Absolute paths (including mapped drive letters like 'Z:\\...' and UNC
      paths like '\\\\host\\share\\...') are canonicalized: mapped drives are
      translated to their UNC share via DRIVE_MAP, and the drive/share anchor is
      resolved so mapped-drive and UNC forms compare equal.
    - Access is granted if the resolved path is inside ANY allowed root.
    Inner symlinks/junctions are NOT followed, keeping the sandbox strict.
    """
    from sankalit_mcp import config

    path = Path(relative_or_abs_path)

    # Relative (no drive, not absolute) -> base on the primary workspace root.
    if not path.is_absolute() and not path.drive:
        base = getattr(config, "WORKSPACE_ROOT", None) or _allowed_roots(config)[0]
        combined = Path(os.path.normpath(base / path))
    else:
        # Translate mapped drive letters + canonicalize the anchor, then
        # normalize '.' / '..' lexically (without following symlinks).
        translated = config.canonicalize(path)
        combined = Path(os.path.normpath(translated))

    for root in _allowed_roots(config):
        root_canon = Path(os.path.normpath(config.canonicalize(root)))
        try:
            combined.relative_to(root_canon)
            return combined
        except ValueError:
            continue

    allowed = [str(config.canonicalize(r)) for r in _allowed_roots(config)]
    raise ValueError(
        f"Access denied: '{path}' is outside allowed workspace roots {allowed}"
    )
