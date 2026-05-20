#!/usr/bin/env python3
"""Build and deploy jasonsun.org.

Usage:
    python3 release.py              # build + verify + deploy
    python3 release.py build        # build only
    python3 release.py deploy       # deploy only
    python3 release.py tts          # regenerate audio + build + verify + deploy
    python3 release.py verify       # check paragraph IDs, timestamps, audio sync
    python3 release.py setup        # install dependencies with uv
    python3 release.py clean        # convert stale WAVs to OGG, remove temp files
"""

import json
import os
import re
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

NUM_CHAPTERS = 6


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


def verify():
    """Check that paragraph IDs, timestamps, and audio sync are all wired correctly."""
    print("\n--- Verify ---")
    errors = []

    book = VISION_DIR / "book.html"
    if not book.exists():
        print("  FAIL: book.html not found (run build first)")
        sys.exit(1)

    html = book.read_text()

    # 1. Paragraph IDs per chapter
    print("  Checking paragraph IDs...")
    para_counts = {}
    for ch in range(1, NUM_CHAPTERS + 1):
        ids = [int(x) for x in re.findall(rf'id="ab-{ch}-(\d+)"', html)]
        if not ids:
            errors.append(f"ch{ch}: no ab- paragraph IDs found")
            continue
        expected = list(range(max(ids) + 1))
        missing = set(expected) - set(ids)
        if missing:
            errors.append(f"ch{ch}: missing paragraph IDs: {sorted(missing)[:5]}...")
        para_counts[ch] = len(ids)
        print(f"    ch{ch}: {len(ids)} paragraphs (ab-{ch}-0 .. ab-{ch}-{max(ids)})")

    # 2. Alignment data embedded
    print("  Checking alignment data...")
    m = re.search(r"var apAlignments = ({.*?});", html, re.DOTALL)
    if not m:
        errors.append("no apAlignments found in book.html")
    else:
        alignments = json.loads(m.group(1))
        for ch in range(1, NUM_CHAPTERS + 1):
            key = str(ch)
            if key not in alignments:
                errors.append(f"ch{ch}: no alignment data")
                continue
            timings = alignments[key]
            n_ts = len(timings)
            n_para = para_counts.get(ch, 0)
            n_null = sum(1 for t in timings if t is None)
            if n_ts != n_para:
                errors.append(f"ch{ch}: {n_ts} timestamps vs {n_para} paragraph IDs")
            if n_null > 0:
                errors.append(f"ch{ch}: {n_null} paragraphs with no audio")
            print(f"    ch{ch}: {n_ts} timestamps, {n_ts - n_null} with audio")

    # 3. Click-to-seek handler
    print("  Checking click-to-seek handler...")
    if 'closest(\'p[id^="ab-"]' not in html and "closest('p[id^=\"ab-\"]" not in html:
        errors.append("click-to-seek handler not found")
    else:
        print("    click handler: OK")

    # 4. Sync function
    print("  Checking paragraph sync function...")
    if "function apSyncParagraph" not in html:
        errors.append("apSyncParagraph function not found")
    else:
        print("    sync function: OK")

    # 5. Audio files exist
    print("  Checking audio files...")
    audio_dir = VISION_DIR / "audio"
    manifest_path = audio_dir / "manifest.json"
    if not manifest_path.exists():
        errors.append("audio/manifest.json not found")
    else:
        manifest = json.loads(manifest_path.read_text())
        total = 0
        for ch_meta in manifest.get("chapters", []):
            mp3 = audio_dir / ch_meta["file"]
            dur = ch_meta.get("duration", 0)
            if not mp3.exists():
                errors.append(f"{ch_meta['file']} missing")
            else:
                size_mb = mp3.stat().st_size / 1024 / 1024
                print(f"    {ch_meta['file']}: {size_mb:.1f} MB, {dur:.0f}s")
                total += dur
        print(f"    total: {total:.0f}s ({total/3600:.1f} hours)")

    # 6. Timestamp files
    print("  Checking timestamp files...")
    ts_dir = VISION_DIR / "timestamps"
    slugs = {
        1: "part01-world-changed", 2: "part02-the-void", 3: "part03-the-pattern",
        4: "part04-the-stack", 5: "part05-transitions", 6: "part06-what-comes-next",
    }
    for ch, slug in slugs.items():
        ts_file = ts_dir / f"{slug}.json"
        if not ts_file.exists():
            errors.append(f"timestamps/{slug}.json missing")
            continue
        ts_data = json.loads(ts_file.read_text())
        if ts_data and isinstance(ts_data[0], dict):
            errors.append(f"ch{ch}: timestamps still in old Whisper format")

    # 7. No stale WAVs
    print("  Checking for stale WAVs...")
    cache_dir = VISION_DIR / "audio-cache"
    stale_wavs = list(cache_dir.glob("*.wav")) if cache_dir.exists() else []
    temp_wavs = list(audio_dir.glob("*.wav")) if audio_dir.exists() else []
    if stale_wavs:
        errors.append(f"{len(stale_wavs)} WAV files in audio-cache/ (run clean)")
    if temp_wavs:
        errors.append(f"{len(temp_wavs)} WAV files in audio/ (run clean)")
    if not stale_wavs and not temp_wavs:
        print("    no stale WAVs")

    # 8. TTS paragraph extraction matches build.py
    print("  Checking TTS paragraph extraction...")
    result = subprocess.run(
        ["python3", str(VISION_DIR / "tts.py"), "verify"],
        capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        errors.append("tts.py verify failed")
        print(f"    {result.stdout.strip()}")
    elif "WARNING" in result.stdout:
        errors.append("tts.py paragraph extraction mismatch")
        print(f"    {result.stdout.strip()}")
    else:
        print("    extraction matches build.py")

    # Summary
    print()
    if errors:
        print(f"  FAIL: {len(errors)} issue(s):")
        for e in errors:
            print(f"    - {e}")
        sys.exit(1)
    else:
        total_paras = sum(para_counts.values())
        print(f"  OK: {total_paras} paragraphs, all tagged, all with timestamps, audio sync wired")


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
        verify()
        deploy()
    elif mode == "verify":
        verify()
    elif mode == "setup":
        setup()
    elif mode == "clean":
        clean()
    elif mode in ("default", "release"):
        build()
        verify()
        deploy()
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
