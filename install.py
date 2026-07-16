#!/usr/bin/env python3
"""Install klipper-cam-sight symlinks into Moonraker and Klipper config dirs."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent

UPDATE_MANAGER_BODY = """\
type: git_repo
primary_branch: main
path: {path}
origin: {origin}
managed_services: klipper moonraker
"""

SYMLINKS = (
    ("component/cam_sight.py", "cam_sight.py"),
    ("klipper_macro/cam_sight.cfg", "cam_sight.cfg"),
)
THEME_FILE = ("mainsail-nav.example.json", "navi.json")


def default_moonraker_components() -> Path:
    return Path(
        os.environ.get(
            "MOONRAKER_COMPONENTS", Path.home() / "moonraker/moonraker/components"
        )
    )


def default_klipper_config() -> Path:
    return Path(os.environ.get("KLIPPER_CONFIG", Path.home() / "printer_data/config"))


def default_moonraker_conf() -> Path:
    if env := os.environ.get("MOONRAKER_CONFIG"):
        return Path(env)
    return default_klipper_config() / "moonraker.conf"


def has_ini_section(text: str, section: str) -> bool:
    return re.search(rf"^\[{re.escape(section)}\]\s*$", text, re.MULTILINE) is not None


def append_ini_section(path: Path, section: str, body: str = "") -> bool:
    """Append an INI section if missing. Returns True when the file changed."""
    if path.is_file():
        text = path.read_text()
        if has_ini_section(text, section):
            return False
        if text and not text.endswith("\n"):
            text += "\n"
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        text = ""

    block = f"\n[{section}]\n"
    if body:
        block += body.rstrip() + "\n"
    path.write_text(text + block)
    return True


def git_origin() -> str | None:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(PLUGIN_ROOT), "remote", "get-url", "origin"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None
    return out or None


def symlink_force(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.is_symlink() or dst.exists():
        dst.unlink()
    dst.symlink_to(src)


def require_dir(path: Path, env_hint: str) -> None:
    if path.is_dir():
        return
    print(f"ERROR: {env_hint} dir not found: {path}", file=sys.stderr)
    print(f"Set {env_hint} or install dependencies first.", file=sys.stderr)
    sys.exit(1)


def configure_moonraker(moonraker_conf: Path) -> list[str]:
    """Enable cam_sight and update_manager in moonraker.conf. Returns manual follow-ups."""
    notes: list[str] = []

    if append_ini_section(moonraker_conf, "cam_sight"):
        print(f"==> Added [cam_sight] to {moonraker_conf}")
    else:
        print(f"==> [cam_sight] already in {moonraker_conf}")

    if has_ini_section(moonraker_conf.read_text(), "update_manager cam_sight"):
        print("==> [update_manager cam_sight] already in moonraker.conf")
        return notes

    origin = git_origin()
    if origin:
        body = UPDATE_MANAGER_BODY.format(
            path=str(PLUGIN_ROOT.expanduser()),
            origin=origin,
        )
        if append_ini_section(moonraker_conf, "update_manager cam_sight", body):
            print(f"==> Added [update_manager cam_sight] to {moonraker_conf}")
            return notes

    notes.append("Add [update_manager cam_sight] to moonraker.conf (see README).")
    return notes


def install_mainsail_nav(klipper_config: Path) -> list[str]:
    """Ensure ~/printer_data/config/.theme exists; write navi.json if missing."""
    local_name, dest_name = THEME_FILE
    theme_dir = klipper_config / ".theme"
    theme_dir.mkdir(parents=True, exist_ok=True)
    src = PLUGIN_ROOT / "docs" / local_name
    dst = theme_dir / dest_name
    if not src.is_file():
        return [f"WARNING: missing {src}"]
    if dst.exists():
        print(f"==> {dst} already exists - merge Cam Sight entry if missing")
        return [
            f"Merge Cam Sight entry into {dst} (see docs/mainsail-nav.example.json)"
        ]
    dst.write_text(src.read_text())
    print(f"==> Wrote Mainsail nav to {dst}")
    return []


def _self_check() -> None:
    import tempfile

    assert has_ini_section("[cam_sight]\n", "cam_sight")
    assert has_ini_section("foo = 1\n[cam_sight]\n", "cam_sight")
    assert not has_ini_section("[cam_sight_extra]\n", "cam_sight")

    path = Path("/tmp/cam_sight_install_test.conf")
    path.write_text("[server]\n")
    assert append_ini_section(path, "cam_sight")
    assert has_ini_section(path.read_text(), "cam_sight")
    assert not append_ini_section(path, "cam_sight")
    path.unlink(missing_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        cfg = Path(tmp) / "config"
        cfg.mkdir()
        assert install_mainsail_nav(cfg) == []
        assert (cfg / ".theme" / "navi.json").is_file()
        assert install_mainsail_nav(cfg)  # already exists → merge note


def install() -> int:
    moonraker_components = default_moonraker_components()
    klipper_config = default_klipper_config()
    moonraker_conf = default_moonraker_conf()

    require_dir(moonraker_components, "MOONRAKER_COMPONENTS")
    require_dir(klipper_config, "KLIPPER_CONFIG")

    print("==> Cam Sight install")
    print(f"    source:     {PLUGIN_ROOT}")
    print(f"    components: {moonraker_components}")
    print(f"    config:     {klipper_config}")
    print(f"    moonraker:  {moonraker_conf}")

    dist = PLUGIN_ROOT / "frontend" / "dist"
    if not dist.is_dir():
        print("WARNING: frontend/dist missing - pull latest from git", file=sys.stderr)

    # Drop pre-rename component symlink if present
    obsolete = moonraker_components / "cam_seek.py"
    if obsolete.is_symlink() or obsolete.exists():
        obsolete.unlink()
        print("==> Removed obsolete cam_seek.py")

    for rel_src, dst_name in SYMLINKS:
        src = PLUGIN_ROOT / rel_src
        if not src.is_file():
            print(f"ERROR: missing install source: {src}", file=sys.stderr)
            return 1
        dst = (
            moonraker_components / dst_name
            if dst_name.endswith(".py")
            else klipper_config / dst_name
        )
        symlink_force(src.resolve(), dst)

    print("==> Symlinks created.")
    print()
    manual = configure_moonraker(moonraker_conf)
    manual.extend(install_mainsail_nav(klipper_config))
    print()
    for note in manual:
        print(note)
    print("Add to printer.cfg:  [include cam_sight.cfg]")
    print(
        "Also add [save_variables] - https://www.klipper3d.org/Config_Reference.html#save_variables"
    )
    print("Toolchange macros:   APPLY_TOOL_OFFSET TOOL=n")
    print("Open UI:             http://<printer>/server/files/cam_sight/")
    print()
    print("Restart Moonraker when done.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        _self_check()
        raise SystemExit(0)
    raise SystemExit(install())
