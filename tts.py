#!/usr/bin/env python3
"""Generate English TTS audio for the vision book using Kokoro am_michael.

Per-paragraph hash-based caching: only regenerates audio for changed/new text.
Produces chapter MP3s and per-paragraph timestamps for build.py alignment.

Usage:
    python3 tts.py              # generate audio + timestamps
    python3 tts.py verify       # verify paragraph extraction matches build.py
"""

import re
import json
import hashlib
import html as htmllib
import subprocess
import numpy as np
import soundfile as sf
import markdown
from pathlib import Path

VISION_DIR = Path(__file__).parent
AUDIO_OUT = VISION_DIR / "audio"
CACHE_DIR = VISION_DIR / "audio-cache"
TS_OUT = VISION_DIR / "timestamps"

VOICE = "am_michael"
SAMPLE_RATE = 24000
PAUSE_SECONDS = 0.6

CHAPTERS = [
    ("part1-world-changed", "The World Has Changed"),
    ("part2-the-void", "The Void"),
    ("part3-the-pattern", "The Pattern"),
    ("part4-the-stack", "What the Stack Requires"),
    ("part5-transitions", "The Transitions"),
    ("part6-what-comes-next", "What Comes Next"),
]

AUDIO_SLUGS = {
    "front-matter": "part00-front-matter",
    "part1-world-changed": "part01-world-changed",
    "part2-the-void": "part02-the-void",
    "part3-the-pattern": "part03-the-pattern",
    "part4-the-stack": "part04-the-stack",
    "part5-transitions": "part05-transitions",
    "part6-what-comes-next": "part06-what-comes-next",
}


def read_mdx(path: Path) -> str:
    text = path.read_text()
    text = re.sub(r"^---\n.*?---\n", "", text, flags=re.DOTALL)
    text = re.sub(r"^\s*import\s+.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*export\s+.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\[([^\]]+)\]\(\./[^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\(\.\./[^)]+\)", r"\1", text)
    return text.strip()


def strip_md(text: str) -> str:
    text = re.sub(r"^#+\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return text.strip()


def cache_key(text: str) -> str:
    key = f"{VOICE}|{SAMPLE_RATE}|{PAUSE_SECONDS}|{text}"
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def extract_narration_units(chapter_num: int, chapter_slug: str, chapter_title: str) -> tuple[list[dict], list[str]]:
    """Extract headings + paragraphs in document order for TTS narration.

    Walks MDX files in the same order as build.py's build_content(), using the
    same markdown extensions, so paragraph indices match ab-{ch}-{idx} IDs exactly.

    Returns (units, para_texts) where:
      units: list of {kind, text, para_idx?} in narration order
      para_texts: ordered paragraph texts (for verification against build.py)
    """
    chapter_dir = VISION_DIR / chapter_slug
    units: list[dict] = []
    para_texts: list[str] = []
    para_idx = 0

    # h1 chapter title
    units.append({"kind": "heading", "text": f"Part {chapter_num}. {chapter_title}"})

    md_converter = markdown.Markdown(extensions=["tables", "fenced_code", "footnotes", "smarty"])

    def process_html(html: str):
        nonlocal para_idx
        for m in re.finditer(r"<(h[1-6]|p)\b[^>]*>(.*?)</\1>", html, re.DOTALL):
            tag = m.group(1)
            content = m.group(2)
            raw_plain = re.sub(r"<[^>]+>", "", content).strip()
            tts_text = htmllib.unescape(raw_plain)
            if not raw_plain or len(raw_plain) < 3:
                continue
            if tag.startswith("h"):
                units.append({"kind": "heading", "text": tts_text})
            else:
                units.append({"kind": "para", "text": tts_text, "para_idx": para_idx})
                para_texts.append(raw_plain)
                para_idx += 1

    # Index/intro (same as build.py: strip first h1, convert remainder)
    index_file = chapter_dir / "index.mdx"
    if index_file.exists():
        text = read_mdx(index_file)
        text = re.sub(r"^#\s+.*$", "", text, count=1, flags=re.MULTILINE).strip()
        if text:
            html = md_converter.convert(text)
            md_converter.reset()
            process_html(html)

    # Section files in sorted order (same as build.py)
    for section_file in sorted(chapter_dir.glob("[0-9]*.mdx")):
        text = read_mdx(section_file)
        first_heading = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        if first_heading:
            heading_text = strip_md(first_heading.group(1))
            units.append({"kind": "heading", "text": heading_text})
            text = text[: first_heading.start()] + text[first_heading.end() :]

        html = md_converter.convert(text)
        md_converter.reset()
        process_html(html)

    return units, para_texts


def extract_front_matter_units() -> tuple[list[dict], list[str]]:
    """Extract abstract + preface narration units for TTS.
    Uses ABSTRACT_PARAGRAPHS from build.py for the abstract,
    and front-matter/preface.mdx for the preface.
    """
    import sys
    sys.path.insert(0, str(VISION_DIR))
    from build import ABSTRACT_PARAGRAPHS

    units: list[dict] = []
    para_texts: list[str] = []
    para_idx = 0

    units.append({"kind": "heading", "text": "Abstract"})
    for p_html in ABSTRACT_PARAGRAPHS:
        raw_plain = re.sub(r'<[^>]+>', '', p_html).strip()
        tts_text = htmllib.unescape(raw_plain)
        units.append({"kind": "para", "text": tts_text, "para_idx": para_idx})
        para_texts.append(raw_plain)
        para_idx += 1

    units.append({"kind": "heading", "text": "Preface"})
    preface_file = VISION_DIR / "front-matter" / "preface.mdx"
    if preface_file.exists():
        text = read_mdx(preface_file)
        text = re.sub(r'^#\s+.*$', '', text, count=1, flags=re.MULTILINE).strip()
        md_converter = markdown.Markdown(extensions=["smarty"])
        html = md_converter.convert(text)
        for m in re.finditer(r"<p\b[^>]*>(.*?)</p>", html, re.DOTALL):
            content = m.group(1)
            raw_plain = re.sub(r"<[^>]+>", "", content).strip()
            tts_text = htmllib.unescape(raw_plain)
            if not raw_plain or len(raw_plain) < 3:
                continue
            units.append({"kind": "para", "text": tts_text, "para_idx": para_idx})
            para_texts.append(raw_plain)
            para_idx += 1

    return units, para_texts


def synthesize_unit(pipeline, text: str) -> np.ndarray | None:
    """Synthesize a single text unit, using cache. Returns numpy audio array."""
    h = cache_key(text)
    cached_ogg = CACHE_DIR / f"{h}.ogg"
    cached_wav = CACHE_DIR / f"{h}.wav"
    if cached_ogg.exists():
        audio, _ = sf.read(str(cached_ogg), dtype="float32")
        return audio
    if cached_wav.exists():
        audio, _ = sf.read(str(cached_wav), dtype="float32")
        sf.write(str(cached_ogg), audio, SAMPLE_RATE, format="OGG", subtype="VORBIS")
        cached_wav.unlink()
        return audio

    chunks = []
    try:
        for _gs, _ps, audio in pipeline(text, voice=VOICE):
            if audio is not None:
                chunks.append(audio.numpy() if hasattr(audio, "numpy") else np.array(audio))
    except Exception as e:
        print(f"    WARN: TTS failed [{text[:60]}]: {e}")
        return None

    if not chunks:
        return None

    combined = np.concatenate(chunks)
    sf.write(str(cached_ogg), combined, SAMPLE_RATE, format="OGG", subtype="VORBIS")
    return combined


def synthesize_chapter(pipeline, units: list[dict]) -> tuple[np.ndarray, list]:
    """Synthesize all narration units for a chapter.

    Returns (audio_array, para_timings) where para_timings[i] = [start, end]
    for paragraph with para_idx=i, matching ab-{ch}-{i} in the HTML.
    """
    all_audio = []
    para_timings: dict[int, list | None] = {}
    current_time = 0.0
    pause = np.zeros(int(SAMPLE_RATE * PAUSE_SECONDS), dtype=np.float32)
    cache_hits = 0
    cache_misses = 0

    for i, unit in enumerate(units):
        h = cache_key(unit["text"])
        was_cached = (CACHE_DIR / f"{h}.ogg").exists() or (CACHE_DIR / f"{h}.wav").exists()

        audio = synthesize_unit(pipeline, unit["text"])
        if audio is None:
            if unit["kind"] == "para":
                para_timings[unit["para_idx"]] = None
            continue

        if was_cached:
            cache_hits += 1
        else:
            cache_misses += 1

        start = current_time
        duration = len(audio) / SAMPLE_RATE
        end = start + duration

        if unit["kind"] == "para":
            para_timings[unit["para_idx"]] = [round(start, 2), round(end, 2)]

        all_audio.append(audio)
        all_audio.append(pause)
        current_time = end + PAUSE_SECONDS

        if (i + 1) % 20 == 0 or i == len(units) - 1:
            print(f"    {i + 1}/{len(units)} units ({current_time:.0f}s) [cache: {cache_hits} hit, {cache_misses} new]")

    if para_timings:
        max_idx = max(k for k in para_timings)
        timings_list = [para_timings.get(j) for j in range(max_idx + 1)]
    else:
        timings_list = []

    if all_audio:
        return np.concatenate(all_audio), timings_list
    return np.array([], dtype=np.float32), timings_list


def wav_to_mp3(wav_path: Path, mp3_path: Path):
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(wav_path),
            "-codec:a", "libmp3lame", "-q:a", "7",
            "-ar", "24000", "-ac", "1",
            str(mp3_path),
        ],
        capture_output=True,
    )


def verify_extraction():
    """Verify paragraph extraction matches build.py without generating audio."""
    import sys

    sys.path.insert(0, str(VISION_DIR))
    from build import build_content, build_front_matter

    print("Running build_content() + build_front_matter() for verification...")
    _, _, build_chapter_paras = build_content()
    _, _, build_fm_paras = build_front_matter()
    build_chapter_paras[0] = build_fm_paras

    ok = True

    def check(label, para_texts, build_paras, units):
        nonlocal ok
        n_h = sum(1 for u in units if u["kind"] == "heading")
        n_p = sum(1 for u in units if u["kind"] == "para")
        if len(para_texts) != len(build_paras):
            ok = False
            print(f"  {label}: MISMATCH count tts={len(para_texts)} build={len(build_paras)}")
            for j in range(min(len(para_texts), len(build_paras))):
                if para_texts[j][:50] != build_paras[j][:50]:
                    print(f"    First diff at idx {j}:")
                    print(f"      tts:   {para_texts[j][:80]}")
                    print(f"      build: {build_paras[j][:80]}")
                    break
        else:
            mismatches = 0
            for a, b in zip(para_texts, build_paras):
                if a != b:
                    mismatches += 1
            if mismatches:
                ok = False
                print(f"  {label}: {mismatches} text mismatches ({n_h}h + {n_p}p)")
            else:
                print(f"  {label}: OK {n_h} headings + {n_p} paragraphs")

    fm_units, fm_paras = extract_front_matter_units()
    check("fm", fm_paras, build_chapter_paras.get(0, []), fm_units)

    for i, (chapter_slug, chapter_title) in enumerate(CHAPTERS, 1):
        units, para_texts = extract_narration_units(i, chapter_slug, chapter_title)
        check(f"ch{i}", para_texts, build_chapter_paras.get(i, []), units)

    if ok:
        print("\nAll chapters verified.")
    else:
        print("\nWARNING: mismatches found. Fix extraction before generating audio.")
    return ok


def synthesize_and_export(pipeline, part_num: int, slug_key: str, label: str, units: list[dict], durations: dict, all_timings: dict):
    """Synthesize a chapter/section, export MP3 + timestamps."""
    n_h = sum(1 for u in units if u["kind"] == "heading")
    n_p = sum(1 for u in units if u["kind"] == "para")
    print(f"  {n_h} headings + {n_p} paragraphs = {len(units)} narration units")

    audio, timings = synthesize_chapter(pipeline, units)
    audio_slug = AUDIO_SLUGS[slug_key]

    if len(audio) > 0:
        wav_path = AUDIO_OUT / f"{audio_slug}.wav"
        mp3_path = AUDIO_OUT / f"{audio_slug}.mp3"

        sf.write(str(wav_path), audio, SAMPLE_RATE)
        duration = len(audio) / SAMPLE_RATE
        durations[part_num] = round(duration, 1)
        print(f"  WAV: {wav_path.name} ({duration:.0f}s)")

        wav_to_mp3(wav_path, mp3_path)
        if mp3_path.exists():
            print(f"  MP3: {mp3_path.name} ({mp3_path.stat().st_size / 1024 / 1024:.1f} MB)")
            wav_path.unlink()

        all_timings[part_num] = timings

        ts_path = TS_OUT / f"{audio_slug}.json"
        ts_path.write_text(json.dumps(timings, indent=2))


def generate_audio():
    """Generate TTS audio with hash-based caching and per-paragraph timestamps."""
    from kokoro import KPipeline
    import sys

    AUDIO_OUT.mkdir(exist_ok=True)
    CACHE_DIR.mkdir(exist_ok=True)
    TS_OUT.mkdir(exist_ok=True)

    sys.path.insert(0, str(VISION_DIR))
    from build import build_content, build_front_matter

    print("Verifying paragraph extraction against build.py...")
    _, _, build_chapter_paras = build_content()
    _, _, build_fm_paras = build_front_matter()
    build_chapter_paras[0] = build_fm_paras

    print("\nLoading Kokoro English pipeline...")
    pipeline = KPipeline(lang_code="a")

    durations = {}
    all_timings = {}
    total_parts = len(CHAPTERS) + 1

    print(f"\n[1/{total_parts}] front-matter (abstract + preface)")
    fm_units, fm_paras = extract_front_matter_units()
    build_paras = build_chapter_paras.get(0, [])
    if len(fm_paras) != len(build_paras):
        print(f"  WARNING: paragraph count mismatch tts={len(fm_paras)} build={len(build_paras)}")
    else:
        mismatches = sum(1 for a, b in zip(fm_paras, build_paras) if a != b)
        if mismatches:
            print(f"  WARNING: {mismatches} paragraph text mismatches")
        else:
            print(f"  Verified: {len(fm_paras)} paragraphs match build.py")
    synthesize_and_export(pipeline, 0, "front-matter", "front-matter", fm_units, durations, all_timings)

    for i, (chapter_slug, chapter_title) in enumerate(CHAPTERS, 1):
        chapter_dir = VISION_DIR / chapter_slug
        if not chapter_dir.exists():
            continue

        print(f"\n[{i + 1}/{total_parts}] {chapter_slug}")
        units, para_texts = extract_narration_units(i, chapter_slug, chapter_title)

        build_paras = build_chapter_paras.get(i, [])
        if len(para_texts) != len(build_paras):
            print(f"  WARNING: paragraph count mismatch tts={len(para_texts)} build={len(build_paras)}")
        else:
            mismatches = sum(1 for a, b in zip(para_texts, build_paras) if a != b)
            if mismatches:
                print(f"  WARNING: {mismatches} paragraph text mismatches")
            else:
                print(f"  Verified: {len(para_texts)} paragraphs match build.py")

        synthesize_and_export(pipeline, i, chapter_slug, chapter_slug, units, durations, all_timings)

    manifest = {
        "title": "Trust at Scale",
        "subtitle": "The missing infrastructure for the AI economy",
        "voice": VOICE,
        "chapters": [
            {
                "part": 0,
                "title": "Abstract & Preface",
                "file": f"{AUDIO_SLUGS['front-matter']}.mp3",
                "duration": durations.get(0, 0),
            }
        ] + [
            {
                "part": idx,
                "title": title,
                "file": f"{AUDIO_SLUGS[slug]}.mp3",
                "duration": durations.get(idx, 0),
            }
            for idx, (slug, title) in enumerate(CHAPTERS, 1)
        ],
        "total_duration": round(sum(durations.values()), 1),
    }
    manifest_path = AUDIO_OUT / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"\nManifest: {manifest_path}")

    return durations, all_timings


def main():
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        verify_extraction()
        return

    generate_audio()


if __name__ == "__main__":
    main()
