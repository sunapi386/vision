#!/usr/bin/env python3
"""Build and deploy jasonsun.org.

Usage:
    python3 release.py              # build + verify + deploy
    python3 release.py build        # build only
    python3 release.py deploy       # deploy only
    python3 release.py tts          # regenerate audio + build + verify + deploy
    python3 release.py verify       # check paragraph IDs, timestamps, audio sync
    python3 release.py stats        # fetch and summarize analytics
    python3 release.py print        # build + generate print-ready PDF for KDP
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
    "vault.html",
    "book.pdf",
    "analytics.html",
    "china-ai.html",
    "slides.html",
    "dir.html",
    "maye.html",
    "ai-clinical.html",
    "sw.js",
    "sw-zh.js",
]

DEPLOY_DIRS = [
    "audio",
    "audio-zh",
    "slides",
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

    # spacy model (Kokoro dependency) - install if missing
    print("  Checking spacy model...")
    try:
        result = subprocess.run(
            [sys.executable, "-c", "import spacy; spacy.load('en_core_web_sm')"],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            print("  Installing en_core_web_sm...")
            run([uv, "pip", "install", "--break-system-packages",
                 "https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl"])
        else:
            print("  en_core_web_sm: OK")
    except Exception as e:
        print(f"  WARNING: spacy check failed: {e}")

    # ffmpeg (required for MP3 export via pydub/soundfile)
    print("  Checking ffmpeg...")
    if shutil.which("ffmpeg"):
        print("  ffmpeg: OK")
    else:
        print("  WARNING: ffmpeg not found. TTS MP3 export will fail.")
        print("  Install it: sudo apt install ffmpeg")

    print("\nSetup complete. Run 'python3 release.py' to build and deploy.")


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

    # 1. Paragraph IDs per chapter (0 = front-matter, 1-6 = parts)
    print("  Checking paragraph IDs...")
    para_counts = {}
    for ch in range(0, NUM_CHAPTERS + 1):
        label = "fm" if ch == 0 else f"ch{ch}"
        ids = [int(x) for x in re.findall(rf'id="ab-{ch}-(\d+)"', html)]
        if not ids:
            errors.append(f"{label}: no ab- paragraph IDs found")
            continue
        expected = list(range(max(ids) + 1))
        missing = set(expected) - set(ids)
        if missing:
            errors.append(f"{label}: missing paragraph IDs: {sorted(missing)[:5]}...")
        para_counts[ch] = len(ids)
        print(f"    {label}: {len(ids)} paragraphs (ab-{ch}-0 .. ab-{ch}-{max(ids)})")

    # 2. Alignment data embedded
    print("  Checking alignment data...")
    m = re.search(r"var apAlignments = ({.*?});", html, re.DOTALL)
    if not m:
        errors.append("no apAlignments found in book.html")
    else:
        alignments = json.loads(m.group(1))
        for ch in range(0, NUM_CHAPTERS + 1):
            label = "fm" if ch == 0 else f"ch{ch}"
            key = str(ch)
            if key not in alignments:
                errors.append(f"{label}: no alignment data")
                continue
            timings = alignments[key]
            n_ts = len(timings)
            n_para = para_counts.get(ch, 0)
            n_null = sum(1 for t in timings if t is None)
            if n_ts != n_para:
                errors.append(f"{label}: {n_ts} timestamps vs {n_para} paragraph IDs")
            if n_null > 0:
                errors.append(f"{label}: {n_null} paragraphs with no audio")
            print(f"    {label}: {n_ts} timestamps, {n_ts - n_null} with audio")

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
        0: "part00-front-matter",
        1: "part01-world-changed", 2: "part02-the-void", 3: "part03-the-pattern",
        4: "part04-the-stack", 5: "part05-transitions", 6: "part06-what-comes-next",
    }
    for ch, slug in slugs.items():
        label = "fm" if ch == 0 else f"ch{ch}"
        ts_file = ts_dir / f"{slug}.json"
        if not ts_file.exists():
            errors.append(f"timestamps/{slug}.json missing")
            continue
        ts_data = json.loads(ts_file.read_text())
        if ts_data and isinstance(ts_data[0], dict):
            errors.append(f"{label}: timestamps still in old Whisper format")

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


def stats():
    """Fetch and summarize analytics from the server."""
    from collections import defaultdict
    from datetime import datetime, timedelta

    print("\n--- Stats ---")
    host = resolve_host()

    result = subprocess.run(
        ["ssh", host, f"cat {DEPLOY_PATH}analytics.jsonl"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print("  Could not read analytics.jsonl from server")
        sys.exit(1)

    events = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except Exception:
            pass

    if not events:
        print("  No events recorded yet")
        return

    now = datetime.fromisoformat(events[-1]["ts"].replace("Z", "+00:00"))
    day_ago = now - timedelta(days=1)
    week_ago = now - timedelta(days=7)

    sessions = defaultdict(lambda: {"events": [], "pages": set(), "max_scroll": 0, "audio_chapters": set(), "duration": 0})
    event_counts = defaultdict(int)
    section_views = defaultdict(int)
    audio_plays = defaultdict(int)

    for e in events:
        event_counts[e.get("event", "unknown")] += 1
        sid = e.get("sid")
        if sid:
            sessions[sid]["events"].append(e)
            sessions[sid]["pages"].add(e.get("page", ""))
            if e.get("event") == "heartbeat":
                sessions[sid]["max_scroll"] = max(sessions[sid]["max_scroll"], e.get("scroll", 0))
                sessions[sid]["duration"] = max(sessions[sid]["duration"], e.get("elapsed", 0))
            if e.get("event") == "section_view":
                section_views[e.get("section", "")] += 1
            if e.get("event") == "play":
                audio_plays[e.get("chapter", "")] += 1
                sessions[sid]["audio_chapters"].add(e.get("chapter", ""))

    total_sessions = len(sessions)
    recent_sessions = sum(1 for s in sessions.values()
                          if any(e.get("ts", "") > day_ago.isoformat() for e in s["events"]))

    print(f"  Total events: {len(events)}")
    print(f"  Event breakdown: {dict(event_counts)}")
    print(f"  Unique sessions (all time): {total_sessions}")
    print(f"  Sessions (last 24h): {recent_sessions}")

    if sessions:
        durations = [s["duration"] for s in sessions.values() if s["duration"] > 0]
        scrolls = [s["max_scroll"] for s in sessions.values() if s["max_scroll"] > 0]
        listeners = [s for s in sessions.values() if s["audio_chapters"]]

        if durations:
            avg_dur = sum(durations) / len(durations)
            print(f"  Avg session duration: {avg_dur:.0f}s ({avg_dur/60:.1f}min)")
            print(f"  Max session duration: {max(durations)}s ({max(durations)/60:.1f}min)")
        if scrolls:
            print(f"  Avg max scroll: {sum(scrolls)/len(scrolls):.0f}%")
            print(f"  Readers reaching bottom (90%+): {sum(1 for s in scrolls if s >= 90)}/{len(scrolls)}")
        if listeners:
            print(f"  Audio listeners: {len(listeners)}/{total_sessions} sessions")
            print(f"  Avg chapters listened: {sum(len(s['audio_chapters']) for s in listeners)/len(listeners):.1f}")

    if section_views:
        print("\n  Section reach:")
        for section, count in sorted(section_views.items(), key=lambda x: -x[1]):
            print(f"    {section}: {count} viewers")

    if audio_plays:
        print("\n  Audio plays by chapter:")
        for ch, count in sorted(audio_plays.items()):
            print(f"    {ch}: {count} plays")


PRINT_CSS = """
@page {
    size: 6in 9in;
    margin: 0.75in 0.625in 0.75in 0.875in;  /* top right bottom left (left = gutter) */
    @bottom-center {
        content: counter(page);
        font-family: 'Space Grotesk', sans-serif;
        font-size: 9pt;
        color: #888;
    }
}
@page :first { @bottom-center { content: none; } }
@page :blank { @bottom-center { content: none; } }

body {
    font-size: 10.5pt;
    line-height: 1.6;
    color: #1a1a1a;
    background: #fff;
}

/* strip web-only elements */
.site-nav, .progress-bar, .scroll-cue, .audio-player, .audio-player-toggle,
.toc, #audioToggle, .hero-reading-time, .ap-follow,
.resume-toast, .reading-time { display: none !important; }

/* fix dark-theme bold text (shared.css sets [data-theme="dark"] strong to #fff) */
strong { color: #1a1a1a !important; }

/* hero as title page */
.hero {
    min-height: auto; padding: 200pt 0 100pt; text-align: center;
    page-break-after: always; background: none;
}
.hero::before { display: none; }
.hero a, .hero div[style] { display: none !important; }
.hero-eyebrow { color: #666; }
.hero-title { color: #1a1a1a; font-size: 32pt; }
.hero-subtitle { color: #444; font-size: 13pt; }
.hero-author { color: #666; }

/* override dark theme colors for print */
:root, [data-theme="dark"], [data-theme="light"] {
    --bg: #fff; --bg-surface: #f6f6f6; --bg-elevated: #eee;
    --text: #1a1a1a; --text-dim: #444; --text-dimmer: #888;
    --accent: #2563eb; --accent-dim: rgba(37,99,235,0.08);
    --green: #1a7f37; --green-dim: rgba(26,127,55,0.08);
    --orange: #9a6700; --orange-dim: rgba(154,103,0,0.08);
    --red: #cf222e; --red-dim: rgba(207,34,46,0.08);
    --purple: #8250df; --cyan: #0969da;
    --border: #ddd; --border-strong: #ccc;
    --shadow: none;
}

/* page breaks */
.chapter-break { page-break-before: always; padding-top: 80pt; margin-top: 0; }
.chapter-break:first-child { page-break-before: auto; }
.visual-break, .pullquote { page-break-inside: avoid; }
.back-matter { page-break-before: always; }
.back-matter-section + .back-matter-section { page-break-before: always; }
.colophon { page-break-before: always; }
.dedication { page-break-after: always; }
.preface { page-break-after: always; }
.abstract { page-break-after: always; }

/* make animated elements visible */
.fade-in { opacity: 1 !important; transform: none !important; }
.layer-animate { opacity: 1 !important; }
.flywheel-node { opacity: 1 !important; }

/* paragraph click styling off */
p[id^="ab-"] { cursor: default; border-left: none; padding-left: 0; margin-left: 0; }
p[id^="ab-"]:hover { background: none; }

/* article width */
.article { max-width: 100%; padding: 0; }

/* diagram sizing for print */
.arch-diagram, .flywheel-diagram, .envelope-diagram { max-width: 100%; }
.force-grid { grid-template-columns: repeat(3, 1fr); }
.stat-row { flex-direction: row; }

/* links: no underlines, no URL expansion */
a { color: var(--accent); text-decoration: none; }
a[href]::after { content: none; }

/* colophon */
.colophon { font-size: 9pt; }
"""


def print_pdf():
    """Generate a print-ready PDF for KDP (6x9 trim)."""
    import weasyprint

    print("\n--- Print PDF ---")
    book = VISION_DIR / "book.html"
    if not book.exists():
        print("  book.html not found, building first...")
        build()

    html = book.read_text()

    # bake animated counter values: data-count="400">0< → >400<
    html = re.sub(
        r'data-count="(\d+)">\s*0\s*<',
        lambda m: f'data-count="{m.group(1)}">{m.group(1)}<',
        html,
    )

    # bake bar-fill widths
    html = re.sub(
        r'class="bar-fill"\s+data-width="(\d+)"\s+style="([^"]*)"',
        lambda m: f'class="bar-fill" data-width="{m.group(1)}" style="{m.group(2)}; width: {m.group(1)}%"',
        html,
    )

    # strip web-only text
    html = re.sub(r'<p[^>]*>~7 hours.*?</p>', '', html, flags=re.DOTALL)

    # strip <script> blocks
    html = re.sub(r'<script\b[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    # strip <audio> tag
    html = re.sub(r'<audio\b[^>]*>.*?</audio>', '', html, flags=re.DOTALL)

    out = VISION_DIR / "book.pdf"
    print("  Rendering PDF with WeasyPrint (this may take 30-60s)...")
    doc = weasyprint.HTML(string=html, base_url=str(VISION_DIR))
    doc.write_pdf(str(out), stylesheets=[weasyprint.CSS(string=PRINT_CSS)])
    size_mb = out.stat().st_size / 1024 / 1024
    print(f"  Written to {out} ({size_mb:.1f} MB)")


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
    elif mode == "stats":
        stats()
    elif mode == "print":
        build()
        print_pdf()
    elif mode == "setup":
        setup()
    elif mode == "clean":
        clean()
    elif mode in ("default", "release"):
        build()
        print_pdf()
        verify()
        deploy()
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
