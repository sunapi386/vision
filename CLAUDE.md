# jasonsun.org (vision)

Personal site + "Trust at Scale" book. Build with `python3 release.py build`, deploy with `python3 release.py`. Generated outputs (book.html, index.html, book-zh.html, listen.html, stats.html, timestamps/) are gitignored; edit the .mdx sources and index-content.html, never the generated files.

## Writing style

- **Never use em dashes** (U+2014, or the mdash HTML entity), in English or Chinese, in prose, titles, code comments, or strings. They read as AI-written. Restructure the sentence instead: comma, colon, period, parentheses. Chinese text uses full-width comma/colon/semicolon/period in place of the double-dash. `release.py verify` fails if any em dash appears in tracked sources.
- Audio timestamps align per paragraph. Never split or merge paragraphs in the book .mdx files without regenerating TTS (`python3 release.py tts`).
