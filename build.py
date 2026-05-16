#!/usr/bin/env python3
"""Build the vision book into a single-page HTML file."""

import re
import markdown
from pathlib import Path

VISION_DIR = Path(__file__).parent
OUT_FILE = VISION_DIR / "book.html"

CHAPTERS = [
    ("part1-world-changed", "The World Has Changed"),
    ("part2-the-void", "The Void"),
    ("part3-the-pattern", "The Pattern"),
    ("part4-the-stack", "What the Stack Requires"),
    ("part5-transitions", "The Transitions"),
    ("part6-what-comes-next", "What Comes Next"),
]

INTERSTITIALS = {
    1: """
<div class="visual-break">
  <div class="stat-row">
    <div class="stat-card"><div class="stat-number" data-count="400">0</div><div class="stat-label">Billion USD<br>AI infra market by 2028</div></div>
    <div class="stat-card"><div class="stat-number" data-count="150">0</div><div class="stat-unit">+</div><div class="stat-label">Organizations backing<br>Google's A2A protocol</div></div>
    <div class="stat-card"><div class="stat-number" data-count="10">0</div><div class="stat-unit">x</div><div class="stat-label">Cloud API markup<br>vs owned inference</div></div>
  </div>
</div>""",
    2: """
<div class="visual-break">
  <div class="diagram-svg">
    <div class="diagram-title">Seven Forces, One Destination</div>
    <svg viewBox="0 0 700 380" class="arch-diagram">
      <defs>
        <linearGradient id="gc" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="var(--accent)" stop-opacity="0.25"/><stop offset="100%" stop-color="var(--accent)" stop-opacity="0.05"/></linearGradient>
      </defs>
      <rect x="200" y="280" width="300" height="70" rx="14" fill="url(#gc)" stroke="var(--accent)" stroke-width="2" class="layer-animate" style="animation-delay:0.8s"/>
      <text x="350" y="310" text-anchor="middle" fill="var(--accent)" font-family="Space Grotesk,sans-serif" font-size="14" font-weight="700">AGENT ACCOUNTABILITY</text>
      <text x="350" y="330" text-anchor="middle" fill="var(--text-dim)" font-size="11">The infrastructure they all converge on</text>
      <g font-family="Space Grotesk,sans-serif" font-size="11" font-weight="500">
        <rect x="20" y="20" width="120" height="44" rx="8" fill="var(--bg-surface)" stroke="var(--red)" stroke-width="1" class="flywheel-node" style="animation-delay:0s"/><text x="80" y="38" text-anchor="middle" fill="var(--red)" font-size="11" font-weight="600">Regulatory</text><text x="80" y="52" text-anchor="middle" fill="var(--text-dimmer)" font-size="9">EU AI Act, NIST</text>
        <rect x="160" y="20" width="120" height="44" rx="8" fill="var(--bg-surface)" stroke="var(--orange)" stroke-width="1" class="flywheel-node" style="animation-delay:0.1s"/><text x="220" y="38" text-anchor="middle" fill="var(--orange)" font-size="11" font-weight="600">Economic</text><text x="220" y="52" text-anchor="middle" fill="var(--text-dimmer)" font-size="9">CFO cost control</text>
        <rect x="300" y="20" width="120" height="44" rx="8" fill="var(--bg-surface)" stroke="var(--green)" stroke-width="1" class="flywheel-node" style="animation-delay:0.2s"/><text x="360" y="38" text-anchor="middle" fill="var(--green)" font-size="11" font-weight="600">Safety</text><text x="360" y="52" text-anchor="middle" fill="var(--text-dimmer)" font-size="9">Runtime verdicts</text>
        <rect x="440" y="20" width="120" height="44" rx="8" fill="var(--bg-surface)" stroke="var(--purple)" stroke-width="1" class="flywheel-node" style="animation-delay:0.3s"/><text x="500" y="38" text-anchor="middle" fill="var(--purple)" font-size="11" font-weight="600">Legal</text><text x="500" y="52" text-anchor="middle" fill="var(--text-dimmer)" font-size="9">Liability chains</text>
        <rect x="580" y="20" width="100" height="44" rx="8" fill="var(--bg-surface)" stroke="var(--cyan)" stroke-width="1" class="flywheel-node" style="animation-delay:0.4s"/><text x="630" y="38" text-anchor="middle" fill="var(--cyan)" font-size="11" font-weight="600">Environmental</text><text x="630" y="52" text-anchor="middle" fill="var(--text-dimmer)" font-size="9">Carbon per output</text>
        <rect x="90" y="100" width="120" height="44" rx="8" fill="var(--bg-surface)" stroke="var(--text-dim)" stroke-width="1" class="flywheel-node" style="animation-delay:0.5s"/><text x="150" y="118" text-anchor="middle" fill="var(--text-dim)" font-size="11" font-weight="600">Geopolitical</text><text x="150" y="132" text-anchor="middle" fill="var(--text-dimmer)" font-size="9">Sovereign compute</text>
        <rect x="490" y="100" width="120" height="44" rx="8" fill="var(--bg-surface)" stroke="var(--text-dim)" stroke-width="1" class="flywheel-node" style="animation-delay:0.6s"/><text x="550" y="118" text-anchor="middle" fill="var(--text-dim)" font-size="11" font-weight="600">Enterprise</text><text x="550" y="132" text-anchor="middle" fill="var(--text-dimmer)" font-size="9">CISO governance</text>
      </g>
      <line x1="80" y1="64" x2="300" y2="280" stroke="var(--text-dimmer)" stroke-width="0.7" stroke-dasharray="3,3" class="arrow-animate"/>
      <line x1="220" y1="64" x2="320" y2="280" stroke="var(--text-dimmer)" stroke-width="0.7" stroke-dasharray="3,3" class="arrow-animate"/>
      <line x1="360" y1="64" x2="350" y2="280" stroke="var(--text-dimmer)" stroke-width="0.7" stroke-dasharray="3,3" class="arrow-animate"/>
      <line x1="500" y1="64" x2="380" y2="280" stroke="var(--text-dimmer)" stroke-width="0.7" stroke-dasharray="3,3" class="arrow-animate"/>
      <line x1="630" y1="64" x2="420" y2="280" stroke="var(--text-dimmer)" stroke-width="0.7" stroke-dasharray="3,3" class="arrow-animate"/>
      <line x1="150" y1="144" x2="280" y2="280" stroke="var(--text-dimmer)" stroke-width="0.7" stroke-dasharray="3,3" class="arrow-animate"/>
      <line x1="550" y1="144" x2="430" y2="280" stroke="var(--text-dimmer)" stroke-width="0.7" stroke-dasharray="3,3" class="arrow-animate"/>
    </svg>
  </div>
</div>""",
    3: """
<div class="visual-break">
  <div class="timeline">
    <div class="timeline-title">The Accountability Pattern</div>
    <div class="timeline-track">
      <div class="timeline-item"><div class="timeline-dot"></div><div class="timeline-date">1494</div><div class="timeline-text">Double-entry bookkeeping. Commerce becomes auditable.</div></div>
      <div class="timeline-item"><div class="timeline-dot"></div><div class="timeline-date">1973</div><div class="timeline-text">SWIFT. Cross-border banking gets a standard message format.</div></div>
      <div class="timeline-item"><div class="timeline-dot"></div><div class="timeline-date">1995</div><div class="timeline-text">SSL/TLS. The internet becomes safe for transactions.</div></div>
      <div class="timeline-item"><div class="timeline-dot"></div><div class="timeline-date">2013</div><div class="timeline-text">Docker + OCI. Software deployment becomes reproducible.</div></div>
      <div class="timeline-item active"><div class="timeline-dot"></div><div class="timeline-date">202X</div><div class="timeline-text">Agent accountability. The agent economy gets its receipt book.</div></div>
    </div>
  </div>
</div>""",
    4: """
<div class="visual-break">
  <div class="diagram-svg">
    <div class="diagram-title">The Seven-Layer Stack</div>
    <svg viewBox="0 0 700 540" class="arch-diagram">
      <defs>
        <linearGradient id="s1" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="var(--accent)" stop-opacity="0.2"/><stop offset="100%" stop-color="var(--accent)" stop-opacity="0.05"/></linearGradient>
        <linearGradient id="s2" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="var(--green)" stop-opacity="0.2"/><stop offset="100%" stop-color="var(--green)" stop-opacity="0.05"/></linearGradient>
        <linearGradient id="s3" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="var(--orange)" stop-opacity="0.2"/><stop offset="100%" stop-color="var(--orange)" stop-opacity="0.05"/></linearGradient>
        <linearGradient id="s4" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="var(--purple)" stop-opacity="0.2"/><stop offset="100%" stop-color="var(--purple)" stop-opacity="0.05"/></linearGradient>
        <linearGradient id="s5" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="var(--red)" stop-opacity="0.2"/><stop offset="100%" stop-color="var(--red)" stop-opacity="0.05"/></linearGradient>
        <linearGradient id="s6" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="var(--cyan)" stop-opacity="0.2"/><stop offset="100%" stop-color="var(--cyan)" stop-opacity="0.05"/></linearGradient>
      </defs>
      <rect x="80" y="10" width="540" height="60" rx="10" fill="url(#s1)" stroke="var(--accent)" stroke-width="1.5" class="layer-animate" style="animation-delay:0.9s"/>
      <text x="130" y="38" fill="var(--accent)" font-family="Space Grotesk,sans-serif" font-size="12" font-weight="700">M</text>
      <text x="160" y="38" fill="var(--accent)" font-family="Space Grotesk,sans-serif" font-size="12" font-weight="500">MARKETPLACE</text>
      <text x="440" y="38" fill="var(--text-dimmer)" font-size="10">Agent-to-agent commerce</text>
      <rect x="80" y="80" width="540" height="60" rx="10" fill="url(#s6)" stroke="var(--cyan)" stroke-width="1.5" class="layer-animate" style="animation-delay:0.75s"/>
      <text x="130" y="108" fill="var(--cyan)" font-family="Space Grotesk,sans-serif" font-size="12" font-weight="700">A</text>
      <text x="160" y="108" fill="var(--cyan)" font-family="Space Grotesk,sans-serif" font-size="12" font-weight="500">AGENCY</text>
      <text x="440" y="108" fill="var(--text-dimmer)" font-size="10">Identity, authorization, consent</text>
      <rect x="80" y="150" width="540" height="60" rx="10" fill="url(#s5)" stroke="var(--red)" stroke-width="1.5" class="layer-animate" style="animation-delay:0.6s"/>
      <text x="130" y="178" fill="var(--red)" font-family="Space Grotesk,sans-serif" font-size="12" font-weight="700">E</text>
      <text x="160" y="178" fill="var(--red)" font-family="Space Grotesk,sans-serif" font-size="12" font-weight="500">ENFORCEMENT</text>
      <text x="440" y="178" fill="var(--text-dimmer)" font-size="10">Runtime safety verdicts</text>
      <rect x="80" y="220" width="540" height="60" rx="10" fill="url(#s4)" stroke="var(--purple)" stroke-width="1.5" class="layer-animate" style="animation-delay:0.45s"/>
      <text x="130" y="248" fill="var(--purple)" font-family="Space Grotesk,sans-serif" font-size="12" font-weight="700">T</text>
      <text x="160" y="248" fill="var(--purple)" font-family="Space Grotesk,sans-serif" font-size="12" font-weight="500">TRUST</text>
      <text x="440" y="248" fill="var(--text-dimmer)" font-size="10">Reputation from historical transactions</text>
      <rect x="80" y="290" width="540" height="60" rx="10" fill="url(#s3)" stroke="var(--orange)" stroke-width="1.5" class="layer-animate" style="animation-delay:0.3s"/>
      <text x="130" y="318" fill="var(--orange)" font-family="Space Grotesk,sans-serif" font-size="12" font-weight="700">E</text>
      <text x="160" y="318" fill="var(--orange)" font-family="Space Grotesk,sans-serif" font-size="12" font-weight="500">EXCHANGE</text>
      <text x="440" y="318" fill="var(--text-dimmer)" font-size="10">Multi-party settlement</text>
      <rect x="80" y="360" width="540" height="60" rx="10" fill="url(#s2)" stroke="var(--green)" stroke-width="1.5" class="layer-animate" style="animation-delay:0.15s"/>
      <text x="130" y="388" fill="var(--green)" font-family="Space Grotesk,sans-serif" font-size="12" font-weight="700">C</text>
      <text x="160" y="388" fill="var(--green)" font-family="Space Grotesk,sans-serif" font-size="12" font-weight="500">COMPUTE</text>
      <text x="440" y="388" fill="var(--text-dimmer)" font-size="10">Dynamic resource allocation</text>
      <rect x="80" y="430" width="540" height="60" rx="10" fill="var(--accent)" fill-opacity="0.08" stroke="var(--accent)" stroke-width="2" class="layer-animate" style="animation-delay:0s"/>
      <text x="130" y="458" fill="var(--accent)" font-family="Space Grotesk,sans-serif" font-size="12" font-weight="700">A</text>
      <text x="160" y="458" fill="var(--accent)" font-family="Space Grotesk,sans-serif" font-size="12" font-weight="500">ACCOUNTABILITY</text>
      <text x="440" y="458" fill="var(--text-dimmer)" font-size="10">Cost, provenance, governance</text>
      <text x="350" y="520" text-anchor="middle" fill="var(--text-dimmer)" font-family="Space Grotesk,sans-serif" font-size="11" font-style="italic">Each layer builds on the one below</text>
    </svg>
  </div>
</div>""",
    5: """
<div class="visual-break">
  <div class="stat-row">
    <div class="stat-card"><div class="stat-number" data-count="20">0</div><div class="stat-unit">%</div><div class="stat-label">AI maturity declined<br>year-over-year</div></div>
    <div class="stat-card"><div class="stat-number" data-count="72">0</div><div class="stat-unit">%</div><div class="stat-label">AI projects stall<br>at pilot stage</div></div>
    <div class="stat-card"><div class="stat-number" data-count="96">0</div><div class="stat-unit">%</div><div class="stat-label">CIOs involved in<br>AI strategy</div></div>
  </div>
  <div class="stat-source">ServiceNow / Oxford Economics survey of 4,473 organizations, 2025</div>
</div>""",
    6: """
<div class="visual-break cta-section">
  <div class="cta-line fade-in">The revolution always comes first.</div>
  <div class="cta-line fade-in">The accountability layer always comes second.</div>
  <div class="cta-line fade-in">The accountability layer always outlasts the revolution.</div>
  <div class="cta-divider"></div>
  <div class="cta-accent fade-in">The agent economy has its revolution. It is waiting for its ledger.</div>
</div>""",
}

# Visuals injected after specific sections within chapters
# Key: (chapter_num, section_file_num) e.g. (2, 1) = after part2/01-*.mdx
SECTION_VISUALS = {
    (1, 3): """
<div class="visual-break mini-break">
  <div class="force-grid">
    <div class="force-card fade-in">
      <div class="force-num">01</div>
      <div class="force-title">Cloud Lock-in</div>
      <div class="force-desc">Per-token rent. Your data on their servers. Their deprecation schedule.</div>
      <div class="force-bar"><div class="bar-fill" data-width="85" style="--bar-color: var(--red)"></div></div>
      <div class="force-meta">85% of AI spend &rarr; 3 providers</div>
    </div>
    <div class="force-card fade-in">
      <div class="force-num">02</div>
      <div class="force-title">Workflow Gap</div>
      <div class="force-desc">AI does tasks. Nobody automates the full workflow. The 90% between prompts is manual.</div>
      <div class="force-bar"><div class="bar-fill" data-width="72" style="--bar-color: var(--orange)"></div></div>
      <div class="force-meta">72% of AI projects stall at pilot</div>
    </div>
    <div class="force-card fade-in">
      <div class="force-num">03</div>
      <div class="force-title">Hardware Crossover</div>
      <div class="force-desc">Own-inference costs crossed cloud APIs. The gap widens every quarter.</div>
      <div class="force-bar"><div class="bar-fill" data-width="60" style="--bar-color: var(--green)"></div></div>
      <div class="force-meta">10x cost advantage by 2028</div>
    </div>
  </div>
</div>""",
    (4, 2): """
<div class="visual-break mini-break fade-in">
  <div class="reg-grid">
    <div class="reg-item"><div class="reg-flag">EU</div><div class="reg-name">GDPR + AI Act</div></div>
    <div class="reg-item"><div class="reg-flag">CA</div><div class="reg-name">PIPEDA + C-27</div></div>
    <div class="reg-item"><div class="reg-flag">US</div><div class="reg-name">CCPA + state laws</div></div>
    <div class="reg-item"><div class="reg-flag">AU</div><div class="reg-name">Privacy Act reform</div></div>
    <div class="reg-item"><div class="reg-flag">BR</div><div class="reg-name">LGPD</div></div>
    <div class="reg-item"><div class="reg-flag">IN</div><div class="reg-name">DPDP Act</div></div>
  </div>
  <div class="reg-caption">Jurisdictions requiring or proposing data sovereignty measures</div>
</div>""",
    (4, 3): """
<div class="visual-break mini-break fade-in">
  <div class="diagram-svg">
    <div class="diagram-title">The Execution Envelope</div>
    <svg viewBox="0 0 500 200" class="envelope-diagram">
      <rect x="20" y="20" width="460" height="160" rx="12" fill="var(--bg-surface)" stroke="var(--accent)" stroke-width="1.5" stroke-dasharray="6,3"/>
      <text x="250" y="18" text-anchor="middle" fill="var(--accent)" font-family="Space Grotesk,sans-serif" font-size="11" font-weight="600">ExecutionEnvelope</text>
      <rect x="40" y="45" width="130" height="50" rx="8" fill="var(--red)" fill-opacity="0.1" stroke="var(--red)" stroke-width="1"/>
      <text x="105" y="68" text-anchor="middle" fill="var(--red)" font-size="11" font-weight="600">Cost Tree</text>
      <text x="105" y="82" text-anchor="middle" fill="var(--text-dim)" font-size="9">Who spent what</text>
      <rect x="185" y="45" width="130" height="50" rx="8" fill="var(--green)" fill-opacity="0.1" stroke="var(--green)" stroke-width="1"/>
      <text x="250" y="68" text-anchor="middle" fill="var(--green)" font-size="11" font-weight="600">Citations</text>
      <text x="250" y="82" text-anchor="middle" fill="var(--text-dim)" font-size="9">Source &rarr; conclusion</text>
      <rect x="330" y="45" width="130" height="50" rx="8" fill="var(--orange)" fill-opacity="0.1" stroke="var(--orange)" stroke-width="1"/>
      <text x="395" y="68" text-anchor="middle" fill="var(--orange)" font-size="11" font-weight="600">Governance</text>
      <text x="395" y="82" text-anchor="middle" fill="var(--text-dim)" font-size="9">Data handling rules</text>
      <rect x="120" y="115" width="260" height="45" rx="8" fill="var(--accent)" fill-opacity="0.08" stroke="var(--accent)" stroke-width="1"/>
      <text x="250" y="137" text-anchor="middle" fill="var(--accent)" font-size="11" font-weight="600">Execution Context</text>
      <text x="250" y="151" text-anchor="middle" fill="var(--text-dim)" font-size="9">Budget &bull; Jurisdiction &bull; Trace ID &bull; Org chain</text>
    </svg>
  </div>
</div>""",
    (5, 1): """
<div class="visual-break mini-break">
  <div class="stat-row compact">
    <div class="stat-card small fade-in">
      <div class="stat-number" data-count="36">0</div><div class="stat-unit">%</div>
      <div class="stat-label">Currently using<br>agentic AI</div>
    </div>
    <div class="stat-card small fade-in">
      <div class="stat-number" data-count="46">0</div><div class="stat-unit">%</div>
      <div class="stat-label">Considering within<br>12 months</div>
    </div>
    <div class="stat-card small fade-in">
      <div class="stat-number" data-count="69">0</div><div class="stat-unit">%</div>
      <div class="stat-label">Elite CIOs use<br>integrated platforms</div>
    </div>
  </div>
  <div class="stat-source">ServiceNow / Oxford Economics, 4,473 organizations, 2025</div>
</div>""",
    (5, 4): """
<div class="visual-break mini-break fade-in">
  <div class="comparison-chart">
    <div class="comparison-title">Economics: Cloud API vs Sovereign Compute</div>
    <div class="comparison-grid">
      <div class="comparison-col">
        <div class="comparison-header bad">Cloud API</div>
        <div class="comparison-item"><span class="comparison-val">$15-75</span><span class="comparison-desc">per 1M tokens</span></div>
        <div class="comparison-item"><span class="comparison-val">Variable</span><span class="comparison-desc">monthly cost</span></div>
        <div class="comparison-item"><span class="comparison-val">0%</span><span class="comparison-desc">data ownership</span></div>
      </div>
      <div class="comparison-vs">vs</div>
      <div class="comparison-col">
        <div class="comparison-header good">Sovereign</div>
        <div class="comparison-item"><span class="comparison-val">$0.50-2</span><span class="comparison-desc">per 1M tokens (owned)</span></div>
        <div class="comparison-item"><span class="comparison-val">Fixed</span><span class="comparison-desc">hardware amortization</span></div>
        <div class="comparison-item"><span class="comparison-val">100%</span><span class="comparison-desc">data ownership</span></div>
      </div>
    </div>
  </div>
</div>""",
}

PULLQUOTES = {
    2: ("The agent economy is running without paperwork.", "On the void"),
    3: ("Every revolution eventually produces an accountability layer. The accountability layer always outlasts the revolution.", "On the pattern"),
    4: ("The missing layer is not more hardware or better models. It is the infrastructure to account for what agents do.", "On the stack"),
    5: ("Models are commodities. Trust infrastructure is the moat.", "On the transitions"),
    6: ("The question is not whether this infrastructure gets built. It is whether it gets designed.", "On what comes next"),
}


def read_mdx(path: Path) -> str:
    text = path.read_text()
    text = re.sub(r'^---\n.*?---\n', '', text, flags=re.DOTALL)
    text = re.sub(r'^\s*import\s+.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*export\s+.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\[([^\]]+)\]\(\./[^)]+\)', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\(\.\./[^)]+\)', r'\1', text)
    return text.strip()


def slugify(text: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def build_content() -> tuple[str, list[dict]]:
    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'footnotes', 'smarty'])
    sections_html = []
    toc_entries = []

    for i, (chapter_slug, chapter_title) in enumerate(CHAPTERS, 1):
        chapter_dir = VISION_DIR / chapter_slug
        if not chapter_dir.exists():
            continue

        chapter_id = slugify(chapter_title)
        toc_entries.append({"id": chapter_id, "title": f"Part {i}: {chapter_title}", "level": 0})

        if i in PULLQUOTES:
            quote, attr = PULLQUOTES[i]
            sections_html.append(f'<div class="pullquote"><blockquote>{quote}</blockquote><cite>{attr}</cite></div>')

        sections_html.append(f'<section class="chapter-break" id="{chapter_id}">')
        sections_html.append(f'<div class="chapter-number">Part {i}</div>')
        sections_html.append(f'<h1>{chapter_title}</h1>')

        index_file = chapter_dir / "index.mdx"
        if index_file.exists():
            index_text = read_mdx(index_file)
            index_text = re.sub(r'^#\s+.*$', '', index_text, count=1, flags=re.MULTILINE).strip()
            if index_text:
                index_html = md.convert(index_text)
                md.reset()
                sections_html.append(f'<div class="chapter-intro">{index_html}</div>')

        sections_html.append('</section>')

        for section_file in sorted(chapter_dir.glob("[0-9]*.mdx")):
            section_num = int(section_file.stem.split('-')[0])
            section_text = read_mdx(section_file)
            first_heading = re.search(r'^#\s+(.+)$', section_text, re.MULTILINE)
            if first_heading:
                section_title = first_heading.group(1)
                section_id = f"{chapter_id}--{slugify(section_title)}"
                toc_entries.append({"id": section_id, "title": section_title, "level": 1})
                section_text = section_text[:first_heading.start()] + section_text[first_heading.end():]
            else:
                section_title = section_file.stem
                section_id = f"{chapter_id}--{slugify(section_title)}"

            section_html = md.convert(section_text)
            md.reset()

            sections_html.append(f'<section class="subsection fade-in" id="{section_id}">')
            sections_html.append(f'<h2 class="section-title">{section_title}</h2>')
            sections_html.append(section_html)
            sections_html.append('</section>')

            if (i, section_num) in SECTION_VISUALS:
                sections_html.append(SECTION_VISUALS[(i, section_num)])

        if i in INTERSTITIALS:
            sections_html.append(INTERSTITIALS[i])

    return '\n'.join(sections_html), toc_entries


def build_toc_html(entries: list[dict]) -> str:
    items = ['<a href="#abstract" class="toc-chapter">Abstract</a>']
    for entry in entries:
        cls = "toc-chapter" if entry["level"] == 0 else "toc-section"
        items.append(f'<a href="#{entry["id"]}" class="{cls}">{entry["title"]}</a>')
    return '\n'.join(items)


TEMPLATE = """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Agent Accountability: The Missing Infrastructure for the AI Economy</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root, [data-theme="dark"] {
    --bg: #05070c;
    --bg-surface: #0d1117;
    --bg-elevated: #161b22;
    --text: #e6edf3;
    --text-dim: #8b949e;
    --text-dimmer: #484f58;
    --accent: #6aaefc;
    --accent-dim: rgba(106,174,252,0.12);
    --green: #3fb950;
    --green-dim: rgba(63,185,80,0.12);
    --orange: #d29922;
    --orange-dim: rgba(210,153,34,0.12);
    --red: #f85149;
    --purple: #bc8cff;
    --cyan: #39d2c0;
    --border: rgba(255,255,255,0.08);
    --border-strong: rgba(255,255,255,0.15);
    --shadow: 0 2px 12px rgba(0,0,0,0.4);
    --max-width: 720px;
    --toc-width: 220px;
  }
  [data-theme="light"] {
    --bg: #ffffff;
    --bg-surface: #f6f8fa;
    --bg-elevated: #eef1f5;
    --text: #1f2328;
    --text-dim: #59636e;
    --text-dimmer: #8b949e;
    --accent: #0969da;
    --accent-dim: rgba(9,105,218,0.08);
    --green: #1a7f37;
    --green-dim: rgba(26,127,55,0.08);
    --orange: #9a6700;
    --orange-dim: rgba(154,103,0,0.08);
    --red: #cf222e;
    --purple: #8250df;
    --cyan: #0891b2;
    --border: rgba(0,0,0,0.08);
    --border-strong: rgba(0,0,0,0.15);
    --shadow: 0 2px 12px rgba(0,0,0,0.08);
  }

  html { scroll-behavior: smooth; scrollbar-width: thin; scrollbar-color: var(--text-dimmer) transparent; }

  body {
    font-family: 'Inter Tight', -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: clamp(15px, 1.45vw, 18px);
    font-weight: 400;
    line-height: 1.80;
    color: var(--text);
    background: var(--bg);
    -webkit-font-smoothing: antialiased;
    transition: background 0.3s, color 0.3s;
  }

  /* --- Theme toggle --- */
  .theme-toggle {
    position: fixed; top: 20px; right: 20px; z-index: 300;
    width: 40px; height: 40px; border-radius: 50%;
    border: 1px solid var(--border-strong); background: var(--bg-surface);
    color: var(--text-dim); cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; transition: all 0.2s; box-shadow: var(--shadow);
  }
  .theme-toggle:hover { color: var(--accent); border-color: var(--accent); }

  /* --- Progress bar --- */
  .progress-bar { position: fixed; top: 0; left: 0; height: 2px; background: var(--accent); z-index: 200; width: 0; }

  /* --- Hero --- */
  .hero {
    min-height: 100vh; display: flex; flex-direction: column; justify-content: center;
    align-items: center; text-align: center; padding: 40px 24px; position: relative; overflow: hidden;
  }
  .hero::before {
    content: ''; position: absolute; top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: 800px; height: 800px;
    background: radial-gradient(circle, var(--accent-dim) 0%, transparent 60%);
    pointer-events: none; animation: heroPulse 6s ease-in-out infinite;
  }
  @keyframes heroPulse {
    0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.6; }
    50% { transform: translate(-50%, -50%) scale(1.15); opacity: 1; }
  }
  .hero-eyebrow {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 13px; font-weight: 500; letter-spacing: 0.15em;
    text-transform: uppercase; color: var(--accent); margin-bottom: 20px; position: relative;
  }
  .hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(36px, 6vw, 72px); font-weight: 700;
    letter-spacing: -0.04em; line-height: 1.0; margin-bottom: 20px; position: relative;
  }
  .hero-subtitle {
    font-size: clamp(16px, 2vw, 22px); font-weight: 300;
    color: var(--text-dim); max-width: 560px; line-height: 1.5; margin-bottom: 20px;
  }
  .hero-author { font-size: 14px; color: var(--text-dimmer); position: relative; }
  .scroll-cue {
    position: absolute; bottom: 40px; left: 50%; transform: translateX(-50%);
    color: var(--text-dimmer); font-size: 11px; letter-spacing: 0.15em; text-transform: uppercase;
    animation: bounce 2.1s ease-in-out infinite;
  }
  .scroll-cue::after { content: '  \\2193'; }
  @keyframes bounce { 0%,100%{ transform:translateX(-50%) translateY(0); } 50%{ transform:translateX(-50%) translateY(8px); } }

  /* --- Abstract --- */
  .abstract {
    max-width: var(--max-width); margin: 0 auto; padding: 80px 24px 60px;
    border-bottom: 1px solid var(--border);
  }
  .abstract-label {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 12px; font-weight: 600; letter-spacing: 0.12em;
    text-transform: uppercase; color: var(--accent); margin-bottom: 16px;
  }
  .abstract-text {
    font-size: clamp(15px, 1.6vw, 19px); line-height: 1.7; color: var(--text-dim);
  }
  .abstract-text strong { color: var(--text); }

  /* --- TOC Sidebar --- */
  .toc {
    position: fixed; top: 50%; transform: translateY(-50%);
    left: max(16px, calc(50vw - 576px));
    width: var(--toc-width); max-height: 80vh;
    overflow-y: auto; scrollbar-width: none;
    opacity: 0; transition: opacity 0.4s ease; z-index: 100; padding: 8px 0;
  }
  .toc.visible { opacity: 1; }
  .toc::-webkit-scrollbar { display: none; }
  .toc a {
    display: block; text-decoration: none; font-size: 11.5px; line-height: 1.4;
    padding: 3px 12px; color: var(--text-dimmer); border-left: 2px solid transparent;
    transition: color 0.2s, border-color 0.2s;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  .toc a:hover { color: var(--text-dim); }
  .toc a.active { color: var(--accent); border-left-color: var(--accent); }
  .toc .toc-chapter {
    font-family: 'Space Grotesk', sans-serif; font-weight: 600;
    font-size: 11px; letter-spacing: 0.03em; margin-top: 10px; color: var(--text-dim);
  }
  .toc .toc-chapter:first-child { margin-top: 0; }
  .toc .toc-section { padding-left: 20px; font-weight: 400; }

  /* --- Article --- */
  .article { max-width: var(--max-width); margin: 0 auto; padding: 0 24px 160px; }

  /* --- Chapter Break --- */
  .chapter-break { padding: 100px 0 32px; margin-top: 60px; position: relative; }
  .chapter-break::before {
    content: ''; position: absolute; top: 0; left: 50%; transform: translateX(-50%);
    width: 60px; height: 1px; background: var(--border-strong);
  }
  .chapter-break:first-child { margin-top: 0; }
  .chapter-break:first-child::before { display: none; }
  .chapter-number {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 12px; font-weight: 500; color: var(--accent);
    text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 10px;
  }
  .chapter-break h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(28px, 4vw, 48px); font-weight: 700;
    letter-spacing: -0.03em; line-height: 1.1; margin-bottom: 20px;
  }
  .chapter-intro {
    color: var(--text-dim); font-size: clamp(14px, 1.4vw, 17px); line-height: 1.7;
    border-left: 3px solid var(--accent); padding-left: 20px; margin: 12px 0;
  }

  /* --- Subsections --- */
  .subsection { padding: 40px 0 0; }
  .section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(20px, 2.5vw, 28px); font-weight: 600;
    letter-spacing: -0.02em; line-height: 1.2; margin-bottom: 20px;
  }

  /* --- Typography --- */
  h2 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(17px, 2vw, 24px); font-weight: 700; line-height: 1.2;
    margin: 36px 0 14px; padding-top: 14px; border-top: 1px solid var(--border);
  }
  h3 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(14px, 1.55vw, 18px); font-weight: 600;
    color: var(--accent); line-height: 1.3; margin: 28px 0 10px;
  }
  p { margin: 14px 0; }
  strong { font-weight: 600; color: var(--text); }
  [data-theme="dark"] strong { color: #fff; }
  em { font-style: italic; }
  a { color: var(--accent); text-decoration: none; }
  a:hover { text-decoration: underline; }
  blockquote {
    border-left: 2px solid var(--accent); padding: 4px 0 4px 20px;
    margin: 20px 0; color: var(--text-dim); font-style: italic;
  }
  hr { border: none; border-top: 1px solid var(--border); margin: 40px 0; }
  ul, ol { margin: 14px 0 14px 24px; }
  li { margin: 5px 0; }

  /* --- Tables --- */
  table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 14px; }
  th {
    background: var(--bg-surface); text-align: left; padding: 8px 12px;
    font-weight: 600; font-size: 11px; text-transform: uppercase;
    letter-spacing: 0.05em; color: var(--text-dim); border-bottom: 1px solid var(--border);
  }
  td { padding: 8px 12px; border-bottom: 1px solid var(--border); }

  /* --- Code --- */
  code {
    font-family: 'JetBrains Mono', monospace; font-size: 0.88em;
    background: var(--bg-surface); padding: 2px 6px; border-radius: 4px; color: var(--accent);
  }
  pre {
    background: var(--bg-surface); border: 1px solid var(--border);
    border-radius: 8px; padding: 16px 20px; margin: 20px 0; overflow-x: auto; line-height: 1.5;
  }
  pre code { background: none; padding: 0; color: var(--text); }

  /* --- Pullquote --- */
  .pullquote {
    max-width: var(--max-width); margin: 80px auto 40px; padding: 0 24px; text-align: center;
  }
  .pullquote blockquote {
    border: none; padding: 0; margin: 0; font-style: italic;
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(22px, 3vw, 36px); font-weight: 400;
    line-height: 1.3; color: var(--text); letter-spacing: -0.02em;
  }
  [data-theme="dark"] .pullquote blockquote { color: var(--accent); }
  .pullquote cite {
    display: block; margin-top: 12px; font-size: 13px;
    font-style: normal; color: var(--text-dimmer); letter-spacing: 0.05em; text-transform: uppercase;
  }

  /* --- Visual Break (shared) --- */
  .visual-break { max-width: 800px; margin: 60px auto; padding: 0 24px; }

  /* --- Stat cards --- */
  .stat-row { display: flex; gap: 16px; justify-content: center; flex-wrap: wrap; }
  .stat-card {
    flex: 1; min-width: 160px; max-width: 220px;
    background: var(--bg-surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 28px 20px; text-align: center;
    transition: border-color 0.2s, transform 0.2s;
  }
  .stat-card:hover { border-color: var(--accent); transform: translateY(-2px); }
  .stat-number {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 42px; font-weight: 700; color: var(--accent);
    line-height: 1; display: inline;
  }
  .stat-unit {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 28px; font-weight: 400; color: var(--accent); margin-left: 2px;
  }
  .stat-label {
    margin-top: 10px; font-size: 12px; color: var(--text-dim); line-height: 1.4; letter-spacing: 0.02em;
  }
  .stat-source {
    text-align: center; font-size: 11px; color: var(--text-dimmer);
    font-style: italic; margin-top: 16px;
  }

  /* --- SVG Diagrams --- */
  .diagram-svg { text-align: center; }
  .diagram-title {
    font-family: 'Space Grotesk', sans-serif; font-size: 13px; font-weight: 600;
    letter-spacing: 0.1em; text-transform: uppercase; color: var(--text-dim); margin-bottom: 20px;
    text-align: center;
  }
  .arch-diagram, .flywheel-diagram, .margin-chart, .envelope-diagram { max-width: 600px; width: 100%; height: auto; }
  .layer-animate { opacity: 0; animation: layerFade 0.6s ease forwards; }
  @keyframes layerFade { to { opacity: 1; } }
  .flywheel-node { opacity: 0; animation: nodeFade 0.4s ease forwards; }
  @keyframes nodeFade { to { opacity: 1; } }

  /* --- Comparison chart --- */
  .comparison-chart { max-width: 560px; margin: 0 auto; }
  .comparison-chart.compact { max-width: 480px; }
  .comparison-title {
    font-family: 'Space Grotesk', sans-serif; font-size: 13px; font-weight: 600;
    letter-spacing: 0.1em; text-transform: uppercase; color: var(--text-dim);
    text-align: center; margin-bottom: 20px;
  }
  .comparison-grid { display: flex; align-items: stretch; gap: 0; }
  .comparison-col { flex: 1; }
  .comparison-vs {
    display: flex; align-items: center; justify-content: center; padding: 0 16px;
    font-family: 'Space Grotesk', sans-serif; font-size: 14px; font-weight: 600;
    color: var(--text-dimmer); text-transform: uppercase;
  }
  .comparison-header {
    font-family: 'Space Grotesk', sans-serif; font-size: 14px; font-weight: 700;
    padding: 12px 16px; border-radius: 8px 8px 0 0; text-align: center;
  }
  .comparison-header.bad { background: rgba(248,81,73,0.1); color: var(--red); }
  .comparison-header.good { background: rgba(63,185,80,0.1); color: var(--green); }
  .comparison-item {
    padding: 10px 16px; border-bottom: 1px solid var(--border);
    display: flex; flex-direction: column; gap: 2px;
  }
  .comparison-val { font-weight: 600; font-size: 16px; }
  .comparison-desc { font-size: 12px; color: var(--text-dim); }

  /* --- Timeline --- */
  .timeline { max-width: 560px; margin: 0 auto; }
  .timeline-title {
    font-family: 'Space Grotesk', sans-serif; font-size: 13px; font-weight: 600;
    letter-spacing: 0.1em; text-transform: uppercase; color: var(--text-dim);
    text-align: center; margin-bottom: 24px;
  }
  .timeline-track { position: relative; padding-left: 28px; border-left: 2px solid var(--border); }
  .timeline-item { position: relative; padding: 0 0 20px 20px; }
  .timeline-dot {
    position: absolute; left: -34px; top: 4px;
    width: 10px; height: 10px; border-radius: 50%;
    background: var(--bg-surface); border: 2px solid var(--text-dimmer);
  }
  .timeline-item.active .timeline-dot { background: var(--accent); border-color: var(--accent); box-shadow: 0 0 8px var(--accent-dim); }
  .timeline-date { font-family: 'Space Grotesk', sans-serif; font-size: 13px; font-weight: 700; color: var(--accent); }
  .timeline-text { font-size: 13px; color: var(--text-dim); margin-top: 2px; }

  /* --- Force grid (ch2 interstitial) --- */
  .force-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
  .force-card {
    background: var(--bg-surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 24px 20px;
    transition: border-color 0.2s, transform 0.2s;
  }
  .force-card:hover { border-color: var(--accent); transform: translateY(-2px); }
  .force-num {
    font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 500;
    color: var(--text-dimmer); letter-spacing: 0.05em; margin-bottom: 8px;
  }
  .force-title {
    font-family: 'Space Grotesk', sans-serif; font-size: 16px; font-weight: 600;
    color: var(--text); margin-bottom: 8px;
  }
  .force-desc { font-size: 13px; color: var(--text-dim); line-height: 1.5; margin-bottom: 16px; }
  .force-bar {
    height: 4px; background: var(--bg-elevated); border-radius: 2px; overflow: hidden; margin-bottom: 10px;
  }
  .bar-fill {
    height: 100%; width: 0; border-radius: 2px;
    background: var(--bar-color, var(--accent));
    transition: width 1.2s cubic-bezier(0.22, 1, 0.36, 1);
  }
  .force-meta { font-size: 11px; color: var(--text-dimmer); font-style: italic; }

  /* --- Capability grid (ch4 interstitial) --- */
  .cap-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
  .cap-card {
    background: var(--bg-surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 24px 16px; text-align: center;
    transition: border-color 0.2s, transform 0.2s;
  }
  .cap-card:hover { border-color: var(--accent); transform: translateY(-2px); }
  .cap-icon { width: 40px; height: 40px; margin: 0 auto 12px; display: block; }
  .cap-num { line-height: 1; }
  .cap-number {
    font-family: 'Space Grotesk', sans-serif; font-size: 36px; font-weight: 700;
    color: var(--accent); display: inline;
  }
  .cap-plus {
    font-family: 'Space Grotesk', sans-serif; font-size: 24px; font-weight: 400; color: var(--accent);
  }
  .cap-label { font-size: 12px; color: var(--text-dim); margin-top: 8px; line-height: 1.4; }

  /* --- Protocol composition (ch7 interstitial) --- */
  .protocol-compose {
    display: flex; align-items: stretch; justify-content: center; gap: 12px; flex-wrap: wrap;
  }
  .proto-box {
    flex: 1; min-width: 150px; max-width: 200px;
    border-radius: 12px; padding: 24px 16px; text-align: center;
  }
  .proto-aep { background: var(--accent-dim); border: 1px solid var(--accent); }
  .proto-acp { background: var(--green-dim); border: 1px solid var(--green); }
  .proto-result { background: var(--orange-dim); border: 1px solid var(--orange); }
  .proto-name {
    font-family: 'Space Grotesk', sans-serif; font-size: 20px; font-weight: 700; margin-bottom: 4px;
  }
  .proto-aep .proto-name { color: var(--accent); }
  .proto-acp .proto-name { color: var(--green); }
  .proto-result .proto-name { color: var(--orange); }
  .proto-sub { font-size: 12px; color: var(--text-dim); margin-bottom: 14px; }
  .proto-tags { display: flex; flex-wrap: wrap; gap: 6px; justify-content: center; }
  .proto-tags span {
    font-size: 11px; padding: 3px 8px; border-radius: 4px;
    background: var(--bg-surface); color: var(--text-dim); border: 1px solid var(--border);
  }
  .proto-op {
    display: flex; align-items: center; justify-content: center;
    font-family: 'Space Grotesk', sans-serif; font-size: 24px; font-weight: 300;
    color: var(--text-dimmer); min-width: 28px;
  }

  /* --- Traction grid (ch10 interstitial) --- */
  .traction-grid {
    display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;
    max-width: 640px; margin: 0 auto;
  }
  .traction-item {
    display: flex; gap: 12px; align-items: flex-start;
    padding: 16px; background: var(--bg-surface); border: 1px solid var(--border);
    border-radius: 10px; transition: border-color 0.2s;
  }
  .traction-item:hover { border-color: var(--green); }
  .traction-marker {
    width: 8px; height: 8px; min-width: 8px; border-radius: 50%;
    background: var(--green); margin-top: 5px;
    box-shadow: 0 0 8px var(--green-dim);
  }
  .traction-content { display: flex; flex-direction: column; gap: 2px; }
  .traction-content strong { font-size: 14px; color: var(--text); }
  .traction-content span { font-size: 12px; color: var(--text-dim); line-height: 1.4; }

  /* --- CTA closing (ch11 interstitial) --- */
  .cta-section { text-align: center; padding: 80px 24px 40px; max-width: 600px; }
  .cta-line {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(18px, 2.5vw, 28px); font-weight: 400;
    color: var(--text-dim); line-height: 2;
  }
  .cta-divider { width: 40px; height: 2px; background: var(--accent); margin: 28px auto; }
  .cta-accent {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(22px, 3vw, 36px); font-weight: 700;
    color: var(--accent); line-height: 1.3; margin-bottom: 12px;
  }
  .cta-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 14px; color: var(--text-dimmer);
    letter-spacing: 0.1em; margin-top: 24px;
  }

  /* --- Highlight stat (mid-chapter) --- */
  .mini-break { max-width: var(--max-width); }
  .highlight-stat {
    text-align: center; padding: 40px 20px;
    border: 1px solid var(--border); border-radius: 12px;
    background: var(--bg-surface);
  }
  .hs-num { line-height: 1; margin-bottom: 8px; }
  .hs-num .stat-number {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 56px; font-weight: 700; color: var(--accent);
  }
  .hs-pct {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 32px; font-weight: 400; color: var(--accent);
  }
  .hs-text {
    font-size: 15px; color: var(--text-dim); max-width: 420px;
    margin: 0 auto; line-height: 1.5;
  }
  .hs-source {
    font-size: 11px; color: var(--text-dimmer); margin-top: 12px; font-style: italic;
  }

  /* --- Price bars (mid-chapter) --- */
  .price-bars { max-width: 500px; margin: 0 auto; }
  .price-item { margin-bottom: 18px; }
  .price-label {
    font-family: 'Space Grotesk', sans-serif; font-size: 12px; font-weight: 600;
    color: var(--text-dim); margin-bottom: 6px;
  }
  .price-track {
    height: 10px; background: var(--bg-elevated); border-radius: 5px; overflow: hidden; margin-bottom: 4px;
  }
  .price-val { font-size: 13px; color: var(--text); font-weight: 500; }

  /* --- Compact stat variants --- */
  .stat-row.compact { gap: 12px; }
  .stat-card.small { padding: 20px 16px; min-width: 120px; }
  .stat-card.small .stat-number { font-size: 32px; }
  .stat-card.small .stat-unit { font-size: 20px; }

  /* --- Regulation grid (mid-chapter) --- */
  .reg-grid {
    display: flex; flex-wrap: wrap; gap: 10px; justify-content: center;
    max-width: 480px; margin: 0 auto;
  }
  .reg-item {
    display: flex; align-items: center; gap: 8px;
    padding: 8px 14px; background: var(--bg-surface); border: 1px solid var(--border);
    border-radius: 8px; font-size: 13px;
  }
  .reg-flag {
    font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 600;
    color: var(--accent); background: var(--accent-dim); padding: 2px 6px;
    border-radius: 4px; letter-spacing: 0.05em;
  }
  .reg-name { color: var(--text-dim); font-size: 12px; }
  .reg-caption {
    text-align: center; font-size: 11px; color: var(--text-dimmer);
    margin-top: 14px; font-style: italic;
  }

  /* --- Fade-in on scroll --- */
  .fade-in { opacity: 0; transform: translateY(20px); transition: opacity 0.5s ease, transform 0.5s ease; }
  .fade-in.visible { opacity: 1; transform: translateY(0); }

  /* --- Responsive --- */
  @media (max-width: 1180px) { .toc { display: none; } }
  @media (max-width: 640px) {
    .article { padding: 0 16px 120px; }
    .chapter-break { padding: 60px 0 20px; margin-top: 40px; }
    .stat-row { flex-direction: column; align-items: center; }
    .comparison-grid { flex-direction: column; }
    .comparison-vs { padding: 8px 0; }
    .force-grid { grid-template-columns: 1fr; }
    .cap-grid { grid-template-columns: repeat(2, 1fr); }
    .protocol-compose { flex-direction: column; align-items: center; }
    .proto-op { transform: rotate(90deg); padding: 4px 0; }
    .traction-grid { grid-template-columns: 1fr; }
    .reg-grid { flex-direction: column; align-items: center; }
  }

  /* --- Print --- */
  @media print {
    :root, [data-theme="dark"], [data-theme="light"] {
      --bg: #fff; --bg-surface: #f6f6f6; --text: #1a1a1a;
      --text-dim: #555; --text-dimmer: #888; --accent: #2563eb;
      --green: #1a7f37; --orange: #9a6700; --red: #cf222e;
      --border: #ddd; --border-strong: #ccc;
    }
    body { font-size: 11pt; line-height: 1.6; }
    .hero { min-height: auto; padding: 60px 0; page-break-after: always; }
    .hero::before { display: none; }
    .toc, .progress-bar, .scroll-cue, .theme-toggle { display: none; }
    .article { max-width: 100%; padding: 0; }
    .chapter-break { page-break-before: always; padding: 40px 0 20px; margin-top: 0; }
    .visual-break, .pullquote { page-break-inside: avoid; }
    .force-grid, .cap-grid, .protocol-compose, .traction-grid, .cta-section { page-break-inside: avoid; }
    .fade-in { opacity: 1; transform: none; }
    a { color: var(--accent); }
    a[href]::after { content: none; }
  }
</style>
</head>
<body>

<div class="progress-bar" id="progress"></div>
<button class="theme-toggle" id="themeToggle" title="Toggle theme" aria-label="Toggle light/dark theme">&#9788;</button>

<div class="hero">
  <div class="hero-eyebrow">Jason Sun</div>
  <h1 class="hero-title">Agent Accountability</h1>
  <p class="hero-subtitle">The missing infrastructure for the AI economy.</p>
  <p class="hero-author">Jason Sun &middot; May 2026</p>
  <div class="scroll-cue">scroll</div>
</div>

<div class="abstract" id="abstract">
  <div class="abstract-label">Abstract</div>
  <div class="abstract-text">
    <p><strong>AI is reshaping who does work, not just where it happens.</strong> Agents draft contracts, triage patients, process invoices, write reports. The revolution is here. But when Agent A calls Agent B calls Agent C across three organizations &mdash; nobody can account for what happened, what it cost, or whether the data was handled correctly.</p>
    <p>This is not a feature gap. It is a <strong>category gap</strong> &mdash; the same kind of gap that double-entry bookkeeping filled for commerce, that TLS filled for the internet, that container standards filled for software deployment.</p>
    <p>Seven independent forces &mdash; regulatory, economic, safety, legal, environmental, geopolitical, enterprise &mdash; are converging on the same requirement: <strong>standardized agent accountability.</strong> None of them are coordinating. They all need the same infrastructure.</p>
    <p>This document traces the pattern: the world has changed, a void exists in the infrastructure, history shows how that void always gets filled, and a specific seven-layer stack is what the agent economy requires. It examines the transitions &mdash; organizational, human, governmental, economic &mdash; that must happen simultaneously. And it projects what work looks like when the infrastructure exists.</p>
    <p>The accountability layer will be built. The question is whether it is designed intentionally as a coherent stack, or cobbled together from incompatible patches.</p>
  </div>
</div>

<nav class="toc" id="toc">
{toc}
</nav>

<article class="article" id="article">
{content}
</article>

<script>
(function() {
  var toggle = document.getElementById('themeToggle');
  var html = document.documentElement;
  var saved = localStorage.getItem('theme');
  if (saved) { html.setAttribute('data-theme', saved); }
  else if (window.matchMedia('(prefers-color-scheme: light)').matches) { html.setAttribute('data-theme', 'light'); }
  function updateIcon() { toggle.innerHTML = html.getAttribute('data-theme') === 'dark' ? '&#9788;' : '&#9790;'; }
  updateIcon();
  toggle.addEventListener('click', function() {
    var next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    updateIcon();
  });

  var progress = document.getElementById('progress');
  var toc = document.getElementById('toc');
  var heroH = window.innerHeight;

  var tocLinks = toc.querySelectorAll('a');
  var sectionEls = [];
  tocLinks.forEach(function(link) {
    var id = link.getAttribute('href').slice(1);
    var el = document.getElementById(id);
    if (el) sectionEls.push({ el: el, link: link });
  });

  var counters = document.querySelectorAll('[data-count]');
  var counterDone = new Set();
  function animateCounter(el) {
    var target = parseInt(el.dataset.count);
    var duration = 1200;
    var start = performance.now();
    function tick(now) {
      var p = Math.min((now - start) / duration, 1);
      var ease = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(target * ease);
      if (p < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  var fadeEls = document.querySelectorAll('.fade-in');
  var fadeObs = new IntersectionObserver(function(entries) {
    entries.forEach(function(e) {
      if (e.isIntersecting) { e.target.classList.add('visible'); fadeObs.unobserve(e.target); }
    });
  }, { threshold: 0.08 });
  fadeEls.forEach(function(el) { fadeObs.observe(el); });

  var counterObs = new IntersectionObserver(function(entries) {
    entries.forEach(function(e) {
      if (e.isIntersecting && !counterDone.has(e.target)) {
        counterDone.add(e.target);
        animateCounter(e.target);
      }
    });
  }, { threshold: 0.5 });
  counters.forEach(function(el) { counterObs.observe(el); });

  // Animated bar fills
  var barFills = document.querySelectorAll('.bar-fill[data-width]');
  var barObs = new IntersectionObserver(function(entries) {
    entries.forEach(function(e) {
      if (e.isIntersecting) {
        e.target.style.width = e.target.dataset.width + '%';
        barObs.unobserve(e.target);
      }
    });
  }, { threshold: 0.3 });
  barFills.forEach(function(el) { barObs.observe(el); });

  function onScroll() {
    var sy = window.scrollY;
    var docH = document.documentElement.scrollHeight - window.innerHeight;
    progress.style.width = (sy / docH * 100) + '%';
    toc.classList.toggle('visible', sy > heroH * 0.7);
    var active = null;
    var threshold = window.innerHeight * 0.15;
    for (var i = sectionEls.length - 1; i >= 0; i--) {
      if (sectionEls[i].el.getBoundingClientRect().top <= threshold) { active = sectionEls[i]; break; }
    }
    tocLinks.forEach(function(l) { l.classList.remove('active'); });
    if (active) { active.link.classList.add('active'); active.link.scrollIntoView({ block: 'nearest' }); }
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  tocLinks.forEach(function(link) {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      var el = document.getElementById(link.getAttribute('href').slice(1));
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });
})();
</script>

</body>
</html>"""


def main():
    print("Building vision book...")
    content, toc_entries = build_content()
    toc_html = build_toc_html(toc_entries)
    html = TEMPLATE.replace("{toc}", toc_html).replace("{content}", content)
    OUT_FILE.write_text(html)
    print(f"Written to {OUT_FILE}")
    print(f"  {len(toc_entries)} TOC entries")
    word_count = len(re.findall(r'\w+', content))
    print(f"  ~{word_count:,} words")


if __name__ == "__main__":
    main()
