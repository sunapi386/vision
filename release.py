#!/usr/bin/env python3
"""Build and deploy jasonsun.org.

Usage:
    python3 release.py              # build + deploy
    python3 release.py build        # build only (no deploy)
    python3 release.py deploy       # deploy only (skip build)
    python3 release.py tts          # regenerate audio + build + deploy
    python3 release.py setup        # install dependencies with uv
    python3 release.py clean        # convert stale WAVs to OGG, remove temp files
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

VISION_DIR = Path(__file__).parent

DEPLOY_HOSTS = ["ocean", "192.168.2.244"]
DEPLOY_PATH = "/var/www/jasonsun.org/"

DEPLOY_FILES = [
    "book.html",
    "index.html",
    "book-zh.html",
    "sw.js",
    "sw-zh.js",
]

DEPLOY_DIRS = [
    "audio",
    "audio-zh",
]


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, **kwargs)
    if result.returncode != 0:
        print(f"  FAILED (exit {result.returncode})")
        if result.stderr:
            err = result.stderr if isinstance(result.stderr, str) else result.stderr.decode()
            print(f"  {err.strip()}")
        sys.exit(1)
    return result


def resolve_host() -> str:
    for host in DEPLOY_HOSTS:
        result = subprocess.run(
            ["ping", "-c1", "-W2", host],
            capture_output=True,
        )
        if result.returncode == 0:
            return host
    print(f"Cannot reach any of {DEPLOY_HOSTS}. Are you on the local network?")
    sys.exit(1)


def setup():
    print("\n--- Setup ---")
    uv = shutil.which("uv")
    if not uv:
        print("uv not found. Install it: curl -LsSf https://astral.sh/uv/install.sh | sh")
        sys.exit(1)

    run([uv, "pip", "install", "-e", ".[tts]", "--break-system-packages"],
        cwd=str(VISION_DIR))
    print("\nDependencies installed. Run 'python3 release.py' to build and deploy.")


def clean():
    """Convert any leftover WAV cache files to OGG and remove temp files."""
    print("\n--- Clean ---")
    cache_dir = VISION_DIR / "audio-cache"
    audio_dir = VISION_DIR / "audio"

    wavs = list(cache_dir.glob("*.wav")) if cache_dir.exists() else []
    if wavs:
        import soundfile as sf
        print(f"  Converting {len(wavs)} WAV cache files to OGG...")
        for i, wav in enumerate(wavs):
            ogg = wav.with_suffix(".ogg")
            audio, sr = sf.read(str(wav), dtype="float32")
            sf.write(str(ogg), audio, sr, format="OGG", subtype="VORBIS")
            wav.unlink()
            if (i + 1) % 100 == 0:
                print(f"    {i + 1}/{len(wavs)}")
        print(f"  Converted {len(wavs)} files")

    temp_wavs = list(audio_dir.glob("*.wav")) if audio_dir.exists() else []
    for wav in temp_wavs:
        wav.unlink()
        print(f"  Removed {wav.name}")

    if not wavs and not temp_wavs:
        print("  Nothing to clean")


def build():
    print("\n--- Build ---")
    run(["python3", str(VISION_DIR / "build.py")])


def tts():
    print("\n--- TTS ---")
    env = {**os.environ, "PYTHONUNBUFFERED": "1"}
    run(["python3", str(VISION_DIR / "tts.py")], timeout=7200, env=env)
    clean()


def deploy():
    print("\n--- Deploy ---")
    host = resolve_host()

    for f in DEPLOY_FILES:
        src = VISION_DIR / f
        if not src.exists():
            print(f"  skip {f} (not found)")
            continue
        run(["scp", str(src), f"{host}:{DEPLOY_PATH}"])

    for d in DEPLOY_DIRS:
        src = VISION_DIR / d
        if not src.exists():
            print(f"  skip {d}/ (not found)")
            continue
        run(["rsync", "-az", "--delete", f"{str(src)}/", f"{host}:{DEPLOY_PATH}{d}/"])

    print(f"\nDeployed to {host}:{DEPLOY_PATH}")
    print("Live at https://jasonsun.org")


def main():
    args = sys.argv[1:]
    mode = args[0] if args else "default"

    if mode == "build":
        build()
    elif mode == "deploy":
        deploy()
    elif mode == "tts":
        tts()
        build()
        deploy()
    elif mode == "setup":
        setup()
    elif mode == "clean":
        clean()
    elif mode in ("default", "release"):
        build()
        deploy()
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
