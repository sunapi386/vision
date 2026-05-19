#!/usr/bin/env python3
"""Extract sentence-level timestamps from audiobook MP3s using Whisper."""

import json
import whisper
from pathlib import Path

AUDIO_DIR = Path(__file__).parent / "audio"
OUT_DIR = Path(__file__).parent / "timestamps"

CHAPTERS = [
    "part01-world-changed",
    "part02-the-void",
    "part03-the-pattern",
    "part04-the-stack",
    "part05-transitions",
    "part06-what-comes-next",
]

def main():
    OUT_DIR.mkdir(exist_ok=True)
    model = whisper.load_model("base")

    for ch in CHAPTERS:
        mp3 = AUDIO_DIR / f"{ch}.mp3"
        if not mp3.exists():
            print(f"SKIP {mp3}")
            continue

        print(f"Processing {ch}...")
        result = model.transcribe(
            str(mp3),
            language="en",
            verbose=False,
        )

        segments = []
        for seg in result["segments"]:
            segments.append({
                "start": round(seg["start"], 2),
                "end": round(seg["end"], 2),
                "text": seg["text"].strip(),
            })

        out = OUT_DIR / f"{ch}.json"
        out.write_text(json.dumps(segments, indent=2))
        print(f"  → {len(segments)} segments → {out}")

if __name__ == "__main__":
    main()
