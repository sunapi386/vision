# Trust at Scale

The accountability infrastructure for the agent economy. A book and essay by Jason Sun.

**Live at [jasonsun.org](https://jasonsun.org)**

## Setup

Requires Python 3.10+ and [uv](https://docs.astral.sh/uv/). Also needs `ffmpeg` for audio encoding.

```bash
# Install all dependencies (build + TTS)
python3 release.py setup

# Or manually:
uv pip install -e ".[tts]" --break-system-packages
```

## Quick start

```bash
# Build + deploy to jasonsun.org
python3 release.py

# Build only (no deploy)
python3 release.py build

# Regenerate audio, rebuild, and deploy
python3 release.py tts

# Deploy only (skip build)
python3 release.py deploy

# Just build HTML (no deploy)
python3 build.py

# Verify TTS paragraph alignment without generating audio
python3 tts.py verify
```

## Repository structure

```
.
├── build.py                 # Main build script (book.html + index.html)
├── tts.py                   # English TTS with per-paragraph caching
├── release.py               # Build + deploy to jasonsun.org
├── pyproject.toml           # Python dependencies (use: uv pip install -e ".[tts]")
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
├── audio-cache/             # Per-paragraph TTS cache (gitignored)
├── timestamps/              # Per-paragraph timing data (gitignored)
├── sw.js                    # Service worker (offline support)
├── align.py                 # Legacy Whisper alignment (replaced by tts.py)
└── docs/                    # Build and workflow documentation
```

Each chapter directory contains an `index.mdx` (intro) and numbered section files (`01-*.mdx`, `02-*.mdx`, etc.).

## Build pipeline

See [docs/build-pipeline.md](docs/build-pipeline.md) for details.

1. `build.py` reads MDX sources, converts to HTML via Python-Markdown, tags paragraphs with `ab-{chapter}-{index}` IDs, loads per-paragraph timestamps from `timestamps/`, and produces `book.html` and `index.html`.
2. `tts.py` generates audiobook audio using Kokoro TTS (voice `am_michael`). It caches per-paragraph WAV files by content hash so only changed paragraphs are re-synthesized on subsequent runs. Outputs chapter MP3s and timestamp JSON.

## Audio workflow

See [docs/audio.md](docs/audio.md) for details.

The audiobook uses a delta-safe pipeline: each paragraph and heading is synthesized individually, cached by a hash of its text + voice parameters, then concatenated into chapter MP3s. Editing a single paragraph only regenerates that paragraph's audio on the next `tts.py` run.

## Contact

jason@aceteam.ai
