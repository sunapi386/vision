# Trust at Scale

The accountability infrastructure for the agent economy. A book and essay by Jason Sun.

**Live at [jasonsun.org](https://jasonsun.org)**

## Setup

Requires Python 3.10+ and [uv](https://docs.astral.sh/uv/). Also needs `ffmpeg` for audio encoding.

```bash
# Install all dependencies (build + TTS)
python3 release.py setup

# Or manually:
uv pip install -e ".[tts,tts-zh]" --break-system-packages
```

## Quick start

```bash
python3 release.py              # build + verify + deploy
python3 release.py tts          # regenerate both audiobooks + build + verify + deploy
python3 release.py build        # build only
python3 release.py verify       # check everything without deploying
python3 release.py deploy       # deploy only
python3 release.py clean        # convert stale WAVs to OGG
```

## Repository structure

```
.
├── build.py                 # Shared English and Chinese book builder
├── tts.py                   # English TTS with per-paragraph caching
├── tts_zh.py                # Chinese TTS with per-paragraph caching
├── release.py               # Build + deploy to jasonsun.org
├── pyproject.toml           # Python dependencies (use: uv pip install -e ".[tts,tts-zh]")
├── index-content.html       # Essay page content (jasonsun.org landing)
├── templates/
│   ├── shared.css           # Shared styles (book + essay)
│   ├── shared.js            # Shared JS (theme, scroll, analytics)
│   └── nav.html             # Navigation bar template
├── front-matter/
│   └── preface.mdx
├── part1-world-changed/     # Part 1: The World Has Changed
├── part2-the-void/          # Part 2: The Void
├── part3-the-pattern/       # Part 3: The Pattern
├── part4-the-stack/         # Part 4: What the Stack Requires
├── part5-transitions/       # Part 5: The Transitions
├── part6-what-comes-next/   # Part 6: What Comes Next
├── back-matter/
│   ├── acknowledgments.mdx
│   ├── glossary.mdx
│   ├── whats-next.mdx
│   └── about-author.mdx
├── zh/                      # Chinese translation source
├── audio/                   # Generated English MP3s (gitignored)
├── audio-zh/                # Generated Chinese MP3s (gitignored)
├── audio-cache/             # English narration cache (gitignored)
├── audio-cache-zh/          # Chinese narration cache (gitignored)
├── timestamps/              # English paragraph timings (gitignored)
├── timestamps-zh/           # Chinese paragraph timings (gitignored)
├── sw.js                    # Service worker (offline support)
├── align.py                 # Legacy Whisper alignment (replaced by tts.py)
└── docs/                    # Build and workflow documentation
```

Each chapter directory contains an `index.mdx` (intro) and numbered section files (`01-*.mdx`, `02-*.mdx`, etc.).

## Build pipeline

See [docs/build-pipeline.md](docs/build-pipeline.md) for details.

1. `build.py` reads English and Chinese MDX, tags paragraphs with `ab-{chapter}-{index}` IDs, loads their timestamps, and produces `book.html`, `book-zh.html`, and the English `index.html`.
2. `tts.py` generates English audio with Kokoro voice `am_michael`; `tts_zh.py` generates Chinese audio with voice `zm_yunjian`. Both cache each narration unit by content hash and write chapter MP3s and positional paragraph timestamps.

## Audio workflow

See [docs/audio.md](docs/audio.md) for details.

Both audiobooks cache each paragraph and heading as OGG by text and voice parameters. Editing one paragraph only re-synthesizes that unit on the next `release.py tts` run.

## Verification

`release.py verify` runs automatically before every deploy and checks:

1. Paragraph `ab-{ch}-{idx}` IDs exist and are contiguous in book.html
2. Alignment timestamps match paragraph count per chapter
3. No null timestamps (every paragraph has audio)
4. Click-to-seek handler is wired in the JS
5. `apSyncParagraph` highlight/follow function is present
6. MP3 files exist in `audio/` with valid durations
7. No stale WAV files in cache or output directories
8. TTS paragraph extraction matches build.py ordering

If any check fails, the deploy is blocked. Run `python3 release.py verify` standalone to diagnose.

## Contact

jason@aceteam.ai
