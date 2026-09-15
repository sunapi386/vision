#!/usr/bin/env python3
"""Generate Chinese chapter audio with paragraph timestamps and a text cache.

Usage:
    python3 tts_zh.py verify   # check narration order against the book builder
    python3 tts_zh.py          # synthesize, encode, and write timestamps
"""

import hashlib
import html
import json
import re
import subprocess
import sys
from pathlib import Path

VISION_DIR = Path(__file__).parent
AUDIO_OUT = VISION_DIR / "audio-zh"
CACHE_DIR = VISION_DIR / "audio-cache-zh"
TS_OUT = VISION_DIR / "timestamps-zh"

VOICE = "zm_yunjian"
SAMPLE_RATE = 24000
PAUSE_SECONDS = 0.6


def cache_key(text: str) -> str:
    value = f"{VOICE}|{SAMPLE_RATE}|{PAUSE_SECONDS}|{text}"
    return hashlib.sha256(value.encode()).hexdigest()[:16]


def extract_chapters() -> dict[int, list[dict]]:
    """Use the builder's rendered content and paragraph IDs as narration order."""
    from build import BOOK_ZH, build_content
    from release import ZH_UNVOICED

    content, _, chapter_paras = build_content(BOOK_ZH)
    chapter_starts = list(re.finditer(r'<section class="chapter-break"', content))
    if len(chapter_starts) != len(BOOK_ZH["chapters"]):
        raise RuntimeError("Chinese chapter boundaries do not match the book")

    chapters = {}
    for ch, start in enumerate(chapter_starts, 1):
        end = chapter_starts[ch].start() if ch < len(chapter_starts) else len(content)
        chapter_html = content[start.start():end]
        units = []
        seen = []
        for match in re.finditer(r"<(h[1-6]|p)\b([^>]*)>(.*?)</\1>", chapter_html, re.DOTALL):
            tag, attrs, body = match.groups()
            plain = re.sub(r"<[^>]+>", "", body).strip()
            text = html.unescape(plain)
            if not text:
                continue
            if tag.startswith("h"):
                units.append({"kind": "heading", "text": text})
                continue
            anchor = re.search(r'\bid="ab-(\d+)-(\d+)"', attrs)
            if not anchor:
                continue
            anchor_ch, para_idx = map(int, anchor.groups())
            if anchor_ch != ch:
                raise RuntimeError(f"paragraph ab-{anchor_ch}-{para_idx} is in chapter {ch}")
            expected = chapter_paras[ch][para_idx]
            if plain != expected:
                raise RuntimeError(f"chapter {ch} paragraph {para_idx} differs from the builder")
            seen.append(para_idx)
            units.append({
                "kind": "para",
                "text": text,
                "para_idx": para_idx,
                "silent": para_idx in ZH_UNVOICED.get(ch, []),
            })
        if seen != list(range(len(chapter_paras[ch]))):
            raise RuntimeError(f"chapter {ch} narration paragraph IDs do not match the builder")
        if not any(unit["kind"] == "heading" for unit in units):
            raise RuntimeError(f"chapter {ch} has no narration headings")
        chapters[ch] = units
    return chapters


def verify_extraction() -> bool:
    chapters = extract_chapters()
    for ch, units in chapters.items():
        headings = sum(unit["kind"] == "heading" for unit in units)
        paragraphs = sum(unit["kind"] == "para" for unit in units)
        silent = sum(unit.get("silent", False) for unit in units)
        print(f"  ch{ch}: OK {headings} headings + {paragraphs} paragraphs ({silent} silent)")
    print("All Chinese chapters verified.")
    return True


def synthesize_unit(pipeline, text: str):
    """Return one cached or newly generated 24 kHz mono audio array."""
    import numpy as np
    import soundfile as sf

    cached = CACHE_DIR / f"{cache_key(text)}.ogg"
    if cached.exists():
        audio, rate = sf.read(str(cached), dtype="float32")
        if rate != SAMPLE_RATE or audio.ndim != 1 or len(audio) == 0:
            raise RuntimeError(f"invalid Chinese cache file: {cached}")
        return audio

    chunks = []
    for _gs, _ps, audio in pipeline(text, voice=VOICE):
        if audio is not None:
            chunks.append(audio.numpy() if hasattr(audio, "numpy") else np.asarray(audio))
    if not chunks:
        raise RuntimeError(f"Chinese TTS returned no audio for: {text[:60]}")
    combined = np.concatenate(chunks).astype("float32")
    if len(combined) == 0:
        raise RuntimeError(f"Chinese TTS returned empty audio for: {text[:60]}")
    sf.write(str(cached), combined, SAMPLE_RATE, format="OGG", subtype="VORBIS")
    return combined


def export_chapter(pipeline, chapter: int, units: list[dict], audio_slug: str) -> float:
    """Write chapter audio incrementally and align every book paragraph."""
    import numpy as np
    import soundfile as sf

    pause = np.zeros(int(SAMPLE_RATE * PAUSE_SECONDS), dtype="float32")
    wav_path = AUDIO_OUT / f"{audio_slug}.wav"
    temp_mp3 = AUDIO_OUT / f"{audio_slug}.new.mp3"
    mp3_path = AUDIO_OUT / f"{audio_slug}.mp3"
    timings = [None] * sum(unit["kind"] == "para" for unit in units)
    current_time = 0.0
    try:
        with sf.SoundFile(str(wav_path), mode="w", samplerate=SAMPLE_RATE, channels=1) as wav:
            for index, unit in enumerate(units):
                if unit.get("silent"):
                    continue
                audio = synthesize_unit(pipeline, unit["text"])
                start = current_time
                end = start + len(audio) / SAMPLE_RATE
                if unit["kind"] == "para":
                    timings[unit["para_idx"]] = [round(start, 2), round(end, 2)]
                wav.write(audio)
                wav.write(pause)
                current_time = end + PAUSE_SECONDS
                if (index + 1) % 20 == 0 or index == len(units) - 1:
                    print(f"    {index + 1}/{len(units)} units ({current_time:.0f}s)", flush=True)
        if current_time == 0:
            raise RuntimeError(f"chapter {chapter} has no audio")
        result = subprocess.run(
            ["ffmpeg", "-y", "-i", str(wav_path), "-codec:a", "libmp3lame",
             "-b:a", "64k", str(temp_mp3)],
            capture_output=True, text=True,
        )
        if result.returncode != 0 or not temp_mp3.exists() or temp_mp3.stat().st_size == 0:
            raise RuntimeError(f"chapter {chapter} MP3 encoding failed: {result.stderr[-500:]}")
        temp_mp3.replace(mp3_path)
        (TS_OUT / f"{audio_slug}.json").write_text(json.dumps(timings, indent=2))
        print(f"  wrote {mp3_path.name}: {current_time:.0f}s", flush=True)
        return round(current_time, 1)
    finally:
        wav_path.unlink(missing_ok=True)
        temp_mp3.unlink(missing_ok=True)


def generate_audio():
    from build import AUDIO_SLUGS, BOOK_ZH
    from kokoro import KPipeline

    chapters = extract_chapters()
    AUDIO_OUT.mkdir(exist_ok=True)
    CACHE_DIR.mkdir(exist_ok=True)
    TS_OUT.mkdir(exist_ok=True)
    print("Loading Kokoro Chinese pipeline...", flush=True)
    pipeline = KPipeline(lang_code="z")
    durations = {}
    for ch, (chapter_slug, _) in enumerate(BOOK_ZH["chapters"], 1):
        print(f"\n[{ch}/{len(chapters)}] {chapter_slug}", flush=True)
        durations[ch] = export_chapter(
            pipeline, ch, chapters[ch], AUDIO_SLUGS[chapter_slug]
        )
    manifest = {"durations": durations, "voice": VOICE}
    (AUDIO_OUT / "manifest-zh.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False)
    )
    print("Chinese narration regeneration complete.", flush=True)


def main():
    if sys.argv[1:] == ["verify"]:
        verify_extraction()
    elif not sys.argv[1:]:
        generate_audio()
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
